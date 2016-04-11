from functools import partial
import os.path

from flask import Blueprint

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

from App.lib.fontutils import unicodeBlocks

db = SQLAlchemy()
Base = declarative_base()
name_convention = {"ix": 'ix_%(column_0_label)s',
                   "uq": "uq_%(table_name)s_%(column_0_name)s",
                   "ck": "ck_%(table_name)s_%(constraint_name)s",
                   "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
                   "pk": "pk_%(table_name)s"}

Base.metadata.naming_convention = name_convention

def _bp_factory(mod_name, url_prefix, config_args=None, app=None, **kwargs):
    """ blueprint factory """
    import_root = os.path.abspath(os.path.basename(os.path.dirname(__file__)))
    import_name = '{}/{}'.format(import_root, mod_name)

    options = {'template_folder':'{}/{}/templates'.format(import_root, mod_name), 
               'static_folder':'{}/{}/static'.format(import_root, mod_name),
               'url_prefix':url_prefix}

    args_from_config = {}
    if app and config_args:
        # get values from app.config that need app context
        # and update options dict 
        for opt_name, val_name in config_args.items():
            conf_val = config_args.get(val_name)
            if conf_val:
                args_from_config[opt_name] = conf_val

    if args_from_config:
        options.update(args_from_config)

    if kwargs:
        options.update(kwargs)

    bp = Blueprint(mod_name, import_name, **options) 
    return bp

def load_blueprints(app):
    """ partials are called with app context and registered,
        blueprints are just registered
    """
    with app.app_context():
        for i in Blueprints:
            if isinstance(i, partial):
                kwargs = {}
                if i.keywords.get('config_args'):
                    # get values from config_args to look up in app.config
                    #  and use it to call target func
                    for key, cf in i.keywords.get('config_args').items():
                        val = app.config[cf]
                        kwargs[key] = val

                bp = i(app=app, **kwargs)
                app.register_blueprint(bp)

            if isinstance(i, Blueprint):
                app.register_blueprint(i)

public_bp = _bp_factory('Public', '')
gfont_part = partial(_bp_factory, 'Gfont', '', config_args={'static_folder':'GFONT_ROOT_DIR'})

Blueprints = [public_bp, gfont_part]

ub = unicodeBlocks()
