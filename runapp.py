from App.App import create_app
# this is meant for running app on heroku
app = create_app(config='heroku_conf.py')
