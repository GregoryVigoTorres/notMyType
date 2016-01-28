from pathlib import Path

APP_NAME = 'App'
APP_ROOT = str(Path('__file__').parent.resolve())
APP_TMP = str(Path(APP_ROOT, 'tmp'))
APP_LOGDIR = str(Path(APP_ROOT, 'var', 'log'))
APP_LOGFILE = 'App.log'

SECURITY_BLUEPRINT_NAME = 'Admin'
