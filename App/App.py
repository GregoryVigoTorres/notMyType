import logging

from flask import Flask

from flask_wtf.csrf import CsrfProtect
from flask.ext.assets import (Environment, Bundle)
from webassets.loaders import YAMLLoader
from webassets.filter import get_filter

from flask.ext.security import (Security, SQLAlchemyUserDatastore)

from .core import load_blueprints, db
from .Public import *
from .Admin import index
from .Security import user
from .models.user import (User, Role, user_datastore)



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
    security = Security()
    security.init_app(app, user_datastore, register_blueprint=False)

    load_blueprints(app)

    # assets
    assets_env = Environment(app=app)
    assets_env.from_yaml('assets.yml')

    # print(app.url_map)
    # print(app.blueprints)
    # print(app.blueprints['Gfont'].static_folder)
    # print(app.blueprints['Admin'].template_folder)
    # print(app.blueprints['Public'].template_folder)
    # for i in sorted(app.config.items(), key=lambda i:i[0]):
    #     print(i)
    # print(app.static_folder)

    return app
