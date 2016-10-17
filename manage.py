#! /usr/bin/env python3
import logging
from flask.ext.script import Manager, Command

from App.App import create_app
from commands.get_deps import GetDeps
from commands.dbutils import InitDB, UpdateDB, FixFont
from commands.run_tests import RunTests

from colorama import init as init_colorama
from colorama import Fore, Back, Style
init_colorama(autoreset=True)

from flask.ext.assets import ManageAssets

manager = Manager(create_app)
manager.add_option('-c', '--app-config', dest='config', required=False)
manager.add_command('get_deps', GetDeps())
manager.add_command("assets", ManageAssets())
manager.add_command('initdb', InitDB())
manager.add_command('updatedb', UpdateDB())
manager.add_command('fixfont', FixFont())
manager.add_command('test', RunTests)

if __name__ == '__main__':
    log_fmt = '[notMyType][%(levelname)s] %(lineno)d in %(funcName)s - %(message)s'
    logging.basicConfig(format=log_fmt,
                        level=logging.DEBUG)
    manager.run()
