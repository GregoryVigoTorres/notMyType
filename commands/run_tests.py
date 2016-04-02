import pytest
import sys

from flask import current_app
from flask.ext.script import Command, Option


class RunTests(Command):
    def __init__(self):   
        # self.pytest_opts = ['-x', 'App/tests', '--tb=short']
        self.pytest_opts = ['App/tests', '--tb=short'] ## don't stop on first fail
        super(RunTests, self)

    def run(self):
        pytest.main(self.pytest_opts)
