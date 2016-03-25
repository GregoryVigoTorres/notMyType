import logging

from flask import Flask

from flask_wtf.csrf import CsrfProtect
from flask.ext.assets import Environment

from .core import load_blueprints, db
from .Public import *



csrf = CsrfProtect()
logging.basicConfig(format='Flask App...%(message)s', level=logging.INFO)

def create_app(config=None):
    """ config should be a python file """
    app = Flask(__name__.split('.')[0], instance_relative_config=True)

    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    if config is not None:
        app.config.from_pyfile(config)
        app.logger.info('Using config file: {}'.format(config))

    db.init_app(app)

    #Security
    csrf.init_app(app)

    load_blueprints(app)

    # assets
    assets_env = Environment(app=app)
    assets_env.from_yaml('assets.yml')

    # print(app.url_map)
    # print(app.blueprints)

    return app
