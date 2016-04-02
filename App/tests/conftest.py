import pytest

from App.App import create_app

def pytest_addoption(parser):
    parser.addoption('--app-config', 
                     action='store', 
                     dest='config',
                     default='dev_config.py', 
                     help='--app-config, default dev_config.py')


@pytest.fixture(scope='session')
def app(request):
    """fixture for app object"""                                                                                                                  
    app_config = request.config.getoption('--app-config')

    app = create_app(app_config)
    app.testing = True
    return app
