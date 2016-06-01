# NEVER USE THIS CONFIG WITH A PUBLIC APP                                                                                                         
DEBUG = True
TRAP_BAD_REQUEST_ERRORS = True
USE_RELOADER = True

# flask assets
ASSETS_DEBUG = True
AUTO_BUILD = True
SASS_DEBUG_INFO = True
URL_EXPIRE = True

db_conf = {'username':'gfontapp',
           'password': '',
           'host':'localhost',
           'dbname':'gfonts'}

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{username}:{password}@{host}/{dbname}'.format(**db_conf)
SQLALCHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY = ""

SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = ''
SESSION_PROTECTION = 'strong'
SESSION_COOKIE_NAME = 'gfontsession'
