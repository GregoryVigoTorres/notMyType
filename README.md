notMyType is a Flask/Angular app for viewing and downloading fonts that
I made because I was dissatisfied with other options.

All of the fonts currently in the database are from 
    https://github.com/google/fonts
and are released under free font licenses.


SETUP:
    Edit config files as needed

    Setup database with 
        manage.py initdb 
        and then 
        manage.py updatedb

    alembic init, if you plan on changing things

    Get assets with
        manage.py get_deps
        This command downloads assets in deps.conf
        and optionally writes an assets.yml file


TODO:

    Server setup/config
    > uwsgi or gunicorn + nginx

    Caching

    Fix font count bug with filtered fonts

    Tag fonts somehow to keep track of which ones you've been looking at
    find similar fonts
    > by weight, style, category...

    Convert .ttf fonts to .woff
    Add normalize.css to deps.conf
