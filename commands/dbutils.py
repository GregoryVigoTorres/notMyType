from itertools import groupby
import pprint
import sys
import logging
from pathlib import Path

import sqlalchemy.types as types
from sqlalchemy import inspect

from flask import current_app
from flask.ext.script import Command, Option

from colorama import init as init_colorama
from colorama import Fore, Back
init_colorama(autoreset=True)

from App.core import Base, db
from App.models.public import FontMeta, Font, Category

logger = logging.getLogger(__name__)

class InitDB(Command):
    """ create tables """
    def run(self):
        try:
            with current_app.app_context() as context:
                logger.info(current_app.config.get('SQLALCHEMY_DATABASE_URI'))
                db.create_all(app=current_app)
                logger.info('Database Tables Created')
        except Exception as E:
            logger.warning('ERROR! {}'.format(E))

class UpdateDB(Command):
    """ parse METADATA.pb files and populate database """
    # @staticmethod
    def _parse_pb(self, data):
        """ data is str with METADATA.pb content """
        font_info = False
        meta = {'fonts':[], 'subsets':[]}
        for line in data:
            line = line.replace('"', '')
            if '{' in line:
                font = {}
                font_info = True
            if '}' in line:
                meta['fonts'].append(font)
                font_info = False
            if font_info and '{' not in line:
                k, v = line.split(':', maxsplit=1)
                font[k.strip()] = v.strip()
            if not font_info and '}' not in line :
                kv = line.split(':')
                if 'subset' not in line:
                    meta[kv[0].strip()] = kv[1].strip()
                else:
                    meta['subsets'].append(kv[1].strip())
        ## keys: name, designer, license, category, date_added
        ## can be many subsets, and fonts
        return meta

    def get_or_create_font_objects(self, meta):
        font_objs = []
        for i in meta['fonts']:
            f = db.session.query(Font).filter_by(post_script_name=i['post_script_name']).first()
            if not f:
                f = Font(**i)
                logger.info('New font {}'.format(f))
            font_objs.append(f)

        return font_objs

    def get_or_create_category(self, meta):
        category_obj = db.session.query(Category).filter(Category.Category==meta['category']).first()
        if not category_obj:
            category_obj = Category(Category=meta['category'])
            logging.info('Created category {}'.format(category_obj))
        return category_obj

    def _save_to_db(self, meta, verbose=False):
        """
        metadata format:
        {'license': 'UFL',
         'designer': 'Dalton Maag',
         'subsets': ['menu',
                     'cyrillic',
                     'cyrillic-ext',
                     'greek',
                     'greek-ext',
                     'latin',
                     'latin-ext'],
         'category': 'SANS_SERIF',
         'name': 'Ubuntu',
         'date_added': '2010-12-15'}
        """
        fontmeta = db.session.query(FontMeta).filter_by(name=meta['name']).first()
        if fontmeta is None:
            fontmeta = FontMeta(name=meta['name'],
                                license=meta['license'],
                                designer=meta['designer'],
                                date_added=meta['date_added'])

        fonts = self.get_or_create_font_objects(meta)
        fontmeta.fonts = fonts
        category = self.get_or_create_category(meta)
        fontmeta.category = category

        with db.session.no_autoflush:
            db.session.add(fontmeta)


        try:
            db.session.commit()
            logging.info('{} Saved'.format(fontmeta))
        except Exception as E:
            print(E)


    def run(self):
        """ parse .pb files in Gfont root dir """
        meta_root = Path(current_app.config.get('APP_ROOT')).joinpath(Path(current_app.config.get('GFONT_ROOT_DIR')))
        logger.info(meta_root)
        metafiles = [i for i in meta_root.rglob('METADATA.pb')]
        for fn in metafiles:
            with fn.open() as fd:
                data = fd.readlines()
                meta = self._parse_pb(data)

            self._save_to_db(meta)

class FixFont(Command):
    def run(self):
        """ Fixes fontmeta objects with orphan fonts
            i.e. the fonts have been detached from their fontmeta

            Finds fontmeta by name

            If you need the names of fonts with orphans,
            run the db integrity tests.

        """
        name = input('Enter fontmeta name: ')

        fontmeta = db.session.query(FontMeta).filter(FontMeta.name==name).first()
        if not fontmeta:
            logger.warning(Fore.RED+'{} not found')
            return None

        proceed = input('fix fonts for {} (y/n)'.format(fontmeta))
        if not proceed == 'y':
            return None

        meta_root = Path(current_app.config.get('APP_ROOT')).joinpath(Path(current_app.config.get('GFONT_ROOT_DIR')))
        fontmeta_path = meta_root.joinpath(fontmeta.license.lower()).joinpath(fontmeta.name.lower())
        for i in fontmeta_path.iterdir():
            if i.name == 'METADATA.pb':
                with i.open() as fd:
                    data = fd.readlines()
                    meta = UpdateDB._parse_pb(None, data)
                    UpdateDB._save_to_db(None, meta, verbose=True)
