import sys
import logging

from flask import current_app
from flask.ext.script import Command, Option

from App.core import Base, db

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
