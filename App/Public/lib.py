# import logging
import os.path

from flask import (render_template, 
                   current_app, 
                   url_for) 


def get_font_css(fonts):
    """ fonts for font-family and font-face css """
    license_2_path = {'OFL':'ofl', 'APACHE2':'apache', 'UFL':'ufl'}
    font_styles = []
    for i in fonts:
        for font in i.fonts:
            fn = font.filename
            parent_dir = license_2_path[i.license]
            rel_path = '{}/{}/{}'.format(parent_dir, i.name.lower().replace(' ', ''), fn)

            font_url = url_for('Gfont.static', filename=rel_path)
            font_styles.append((font, font_url))

    fonts_css = render_template('font_faces.css', font_styles=font_styles)

    return fonts_css


def get_font_abs_path(font, fontmeta):
    """ absolute path from font orm object """
    license_2_path = {'OFL':'ofl', 'APACHE2':'apache', 'UFL':'ufl'}
    par_dir = license_2_path[fontmeta.license]
    approot = current_app.config.get('APP_ROOT')
    font_path = os.path.join(approot, 
                             'App', 
                             'Gfont', 
                             par_dir, 
                             font.name.lower().replace(' ', ''), 
                             font.filename)

    return font_path
