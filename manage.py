#! /usr/bin/env python3

from flask.ext.script import Manager, Command

from App.App import create_app
from commands.get_deps import GetDeps
from commands.assets_config import GenDepConfig
from commands.dbutils import InitDB, UpdateDB
from commands.run_tests import RunTests

from flask.ext.assets import ManageAssets

manager = Manager(create_app)
manager.add_option('-c', '--app-config', dest='config', required=False)
manager.add_command('get_deps', GetDeps())
manager.add_command('config_deps', GenDepConfig())
manager.add_command("assets", ManageAssets())
manager.add_command('initdb', InitDB())
manager.add_command('updatedb', UpdateDB())
manager.add_command('test', RunTests)

if __name__ == '__main__':
    manager.run()


