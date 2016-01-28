Flask Template

Generic Flask app with login and a couple blueprints.

Usage:
    git clone repo
    pip install -r requirements.txt
    optionally:
    manage.py get_deps
    manage.py config_deps

    set up database
    alembic init


Includes a couple scripts for downloading and ocnfiguring 3rd party CSS/JS assets, like jquery and bootstrap.

get_deps -> Downloads dependencies specified in deps.conf
config_deps -> Writes assets.yml, used by flask-assets

There are some major bugs with SASS-Bootstrap configuration and building using webassets via flask-assets.
Try using the script generated by manage.py config_deps.
If you're using Bootstrap, you probably need to rename _bootstrap.scss to bootstrap.css, or else sass won't output a file.


TODO:
alembic
