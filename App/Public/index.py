import csv
import logging
from pathlib import Path

from flask import render_template, current_app, url_for

from App.core import public_bp, db
from App.models.public import FontMeta


@public_bp.route('/')
def index():
    """ Public front page """
    fonts = db.session.query(FontMeta).order_by(FontMeta.name).limit(25).all()

    license_2_path = {'OFL':'ofl', 'APACHE2':'apache', 'UFL':'ufl'}

    font_styles = []
    for i in fonts:
        ## later on: de-dupe fonts list
        for font in set(i.fonts):
            fn = font.filename
            parent_dir = license_2_path[i.license]
            rel_path = '{}/{}/{}'.format(parent_dir, i.name.lower().replace(' ', ''), fn)

            font_url = url_for('Gfont.static', filename=rel_path)
            font_styles.append((font, font_url))

    fonts_css = render_template('font_faces.css', font_styles=font_styles)

    tmpl_args = {'title':'GFont viewer', 'fonts': fonts, 'fonts_css':fonts_css}
    return render_template('index.html', **tmpl_args)
