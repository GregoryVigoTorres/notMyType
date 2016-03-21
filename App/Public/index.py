import csv
import logging
import os.path
from pathlib import Path

from flask import render_template, current_app, url_for, request
from fontTools.ttLib import TTFont

from sqlalchemy import and_

from App.core import public_bp, db
from App.models.public import FontMeta, Font

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

@public_bp.route('/getspecimen/<int:fontid>')
def get_specimen(fontid):
    """ generate specimen and get a lot of metadata """
    ## FIX the model to make fontmeta available without weird joins
    font, fontmeta = db.session.query(Font, FontMeta).filter(and_(Font.id==fontid, Font.name==FontMeta.name)).first()
    # if none raise 404
    
    license_2_path = {'OFL':'ofl', 'APACHE2':'apache', 'UFL':'ufl'}
    par_dir = license_2_path[fontmeta.license]
    approot = current_app.config.get('APP_ROOT')
    p = os.path.join(approot, 'App', 'Gfont', par_dir, font.name.lower().replace(' ', ''), font.filename)
    # use a context manager cuz file is opened
    ttf_font = TTFont(file=p)
    # print(ttf_font.keys() )

    codepoints = set()
    for i in ttf_font['cmap'].tables:
        print(i.getEncoding(), i.language, i.platformID, i.platEncID )
        # print(dir(i))
        codepoints.update(i.cmap.items()) ## this is what I need

    ## sort by cp and filter out .notdef names
    cp = sorted([i for i in codepoints if not i[1].startswith('.')], key=lambda i: i[0])

    ## deal with subsets later
    # print(codepoints)
    ## get css @font-face 
    
    return render_template('specimen.html', codepoints=cp)


@public_bp.route('/fontsbyletter/<letter>')
@public_bp.route('/fontsbyletter/<letter>/<int:off_set>')
def fonts_by_letter(letter, off_set=0):
    """ AJAX """
    Limit = 15
    next_offset = off_set+Limit
    if off_set:
        prev_offset = off_set-Limit
    else:
        prev_offset = off_set

    fonts = db.session.query(FontMeta).filter(FontMeta.name.like(letter+'%')).order_by(FontMeta.name).offset(off_set).limit(Limit).all()
    fonts_css = get_font_css(fonts)

    tmpl_args = {'title':'GFont viewer', 
                 'fonts': fonts, 
                 'fonts_css':fonts_css, 
                 'next_offset':next_offset, 
                 'prev_offset':prev_offset,
                 'xhr':request.is_xhr}

    return render_template('index.html', **tmpl_args)

@public_bp.route('/')
@public_bp.route('/getfonts/<int:off_set>')
def index(off_set=0):
    """ Public front page """
    Limit = 15
    next_offset = off_set+Limit
    if off_set:
        prev_offset = off_set-Limit
    else:
        prev_offset = off_set

    fonts = db.session.query(FontMeta).order_by(FontMeta.name).offset(off_set).limit(Limit).all()
    fonts_css = get_font_css(fonts)

    tmpl_args = {'title':'GFont viewer', 
                 'fonts': fonts, 
                 'fonts_css':fonts_css, 
                 'next_offset':next_offset, 
                 'prev_offset':prev_offset,
                 'xhr':request.is_xhr}

    return render_template('index.html', **tmpl_args)
