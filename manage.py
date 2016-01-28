#! /usr/bin/env python3

from flask.ext.script import Manager, Command

from App.App import create_app
from commands.get_deps import GetDeps
from commands.assets_config import GenDepConfig
from commands.init_db import InitDB
from commands.update_db import UpdateDB

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command('get_deps', GetDeps())
manager.add_command('config_deps', GenDepConfig())
manager.add_command('initdb', InitDB())
manager.add_command('updatedb', UpdateDB())

if __name__ == '__main__':
    manager.run()


