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
logger.parent.removeHandler(logger.parent.handlers[0])
logger.parent.propagate =False

lh = logging.StreamHandler()
lh.setLevel(logging.DEBUG)
logformat = logging.Formatter('%(levelname)s'+Fore.CYAN+' in %(funcName)s [%(lineno)i] -'+Fore.YELLOW+' %(message)s')
lh.setFormatter(logformat)
logger.addHandler(lh)

class InitDB(Command):
    """ create tables """
    def run(self):
        try:
            with current_app.app_context() as context:
                logger.info(Fore+CYAN+current_app.config.get('SQLALCHEMY_DATABASE_URI'))
                db.create_all(app=current_app)
                logger.info(Fore.CYAN+'Database Tables Created')
        except Exception as E:
            logger.warning(Fore.RED+'ERROR! {}'.format(E))

class UpdateDB(Command):
    """ parse METADATA.pb files and populate database """
    @staticmethod
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

    @staticmethod
    def _save_to_db(self, meta, verbose=False):
        """ dict with metadata """
        fonts = meta.pop('fonts')
        # get or create font_objs
        font_objs = []
        for i in fonts:
            f = db.session.query(Font).filter_by(post_script_name=i['post_script_name']).first()
            if verbose:
                logger.info('found font {}'.format(f))
            if not f:
                f = Font(**i)
                logger.info('will create font {}'.format(f))

            font_objs.append(f)
            db.session.add(f)

        # get or create category
        category_obj = db.session.query(Category).filter(Category.Category==meta['category']).first()
        if not category_obj:
            meta['category'] = Category(Category=meta['category'])
        else:
            meta['category'] = category_obj

        # get or create fontmeta
        md = db.session.query(FontMeta).filter_by(name=meta['name']).first()
        if md is None:
            if verbose:
                logger.info('{} created'.format(md))
            md = FontMeta(**meta)

        db.session.add(md)

        font_names = [i.full_name for i in md.fonts]
        for i in font_objs:
            if not i.full_name in font_names:
                if verbose:
                    logger.info('{} added to {}'.format(i, md))
                md.fonts.append(i)

        db.session.commit()
        logger.info('{} has been updated'.format(md))
        logger.info('fonts: {}'.format(md.fonts))

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
