from itertools import groupby
import sys
import logging
from pathlib import Path

import sqlalchemy.types as types
from sqlalchemy import inspect

from flask import current_app
from flask.ext.script import Command, Option

from App.core import Base, db
from App.models.public import FontMeta, Font, Category

class InitDB(Command):
    """ create tables """
    def run(self):
        try:
            with current_app.app_context() as context:
                print(current_app.config.get('SQLALCHEMY_DATABASE_URI'))
                db.create_all(app=current_app)
                logging.info('Database Tables Created')
        except Exception as E:
            logging.warning('ERROR! {}'.format(E))

class UpdateDB(Command):
    """ parse METADATA.pb files and populate database """
    def _parse_pd(self, data):
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

    def _save_to_db(self, meta):
        """ dict with metadata """
        fonts = meta.pop('fonts')
        font_objs = [Font(**i) for i in fonts]

        category_obj = db.session.query(Category).filter(Category.Category==meta['category']).first()
        if not category_obj:
            meta['category'] = Category(Category=meta['category'])
        else:
            meta['category'] = category_obj

        md = db.session.query(FontMeta).filter_by(name=meta['name']).first()
        if md is None:
            md = FontMeta(**meta)

        db.session.add(md)

        font_names = [i.full_name for i in md.fonts]
        for i in font_objs:
            if not i.full_name in font_names:
                md.fonts.append(i)

        db.session.commit()
        logging.info('{} has been saved'.format(md))
        logging.info('fonts: {}'.format(md.fonts))


    def run(self):
        """ parse .pb files in Gfont root dir """
        meta_root = Path(current_app.config.get('APP_ROOT')).joinpath(Path(current_app.config.get('GFONT_ROOT_DIR')))
        logging.info(meta_root)
        metafiles = [i for i in meta_root.rglob('METADATA.pb')]
        for fn in metafiles:
            with fn.open() as fd:
                data = fd.readlines()
                meta = self._parse_pd(data)

            self._save_to_db(meta)

