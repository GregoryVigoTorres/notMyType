import os

# db_conf = {'username':'notmytypeapp',
#            'password': 'WetIcnevaitPommoubCoygdimGoygyic',
#            'host':'localhost',
#            'port': 5432,
#            'dbname':'notmytype'}
#
# SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}'.format(**db_conf)
if os.environ.get('DATABASE_URL'):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
else:
    SQLALCHEMY_DATABASE_URI = 'postgres://utysnbynhwhopx:AXxhlYUcjA7eyKRLX1CSzVZym-@ec2-54-243-217-22.compute-1.amazonaws.com:5432/dfqur0enuerhu1'

SQLALCHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY = "negCinRogvuWodBahogcutDojwatyeehiOlAjmibrOtEpIfKekKegUdnocUcCaquaifGasnicuj"

SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'rutrirEyptimOwcocBopan4'
SESSION_PROTECTION = 'strong'
SESSION_COOKIE_NAME = 'notmytype'

