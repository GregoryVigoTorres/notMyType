# import logging
from pathlib import Path
import tempfile
import zipfile

from flask import (render_template, 
                   send_file)

from sqlalchemy import and_

from App.core import (public_bp, db)
from App.models.public import (FontMeta, Font)

from .lib import get_font_abs_path


def add_font_to_zip(font_path, font, zip_tmp, zipdir):
    """ write to temp files """
    font_tmp = tempfile.NamedTemporaryFile(mode='wb')
    with open(font_path, mode='rb') as fd:
        font_tmp.write(fd.read())
        font_tmp.seek(0)
        zip_tmp.write(font_tmp.name, arcname=zipdir+font.filename)
        font_tmp.close()


@public_bp.route('/downloadall/<fontid>')
def download_font_family(fontid):
    """ returns all fonts in family, nicely zipped with relevant CSS 
        fontmeta.name is the name of the directory in the zip file
    """
    fontmeta = db.session.query(FontMeta).get(fontid)

    font_data = {'font_styles': [(f.as_dict, f.filename) for f in fontmeta.fonts]}
    fontcss = render_template('font_faces.css', **font_data)

    tmp_file = tempfile.NamedTemporaryFile(suffix='.fonts.tmp')

    with zipfile.ZipFile(tmp_file, mode='w') as zip_tmp:
        dirname_convention = ''.maketrans({'-':'_', ' ':'_'})
        zipdir = fontmeta.name.translate(dirname_convention)+'/'
        zip_tmp.writestr(zipdir+'/fontface.css', bytes(fontcss, encoding='utf-8'))

        for font in fontmeta.fonts:
            font_path = get_font_abs_path(font, fontmeta)
            add_font_to_zip(font_path, font, zip_tmp, zipdir)

        # get font root, look there for .txt files
        # Licenses and such need to be included in the zip file
        txt_paths = [Path(i) for i in 
                     Path(get_font_abs_path(fontmeta.fonts[0], fontmeta)).parent.iterdir() 
                     if i.suffix in ('.txt', '.html')]
        [zip_tmp.write(str(i), arcname=zipdir+i.name) for i in txt_paths]

    att_name = fontmeta.name.replace(' ', '_')+'.zip'
    tmp_file.seek(0)

    return send_file(tmp_file, as_attachment=True, attachment_filename=att_name)


@public_bp.route('/download/<fontid>')
def download_font(fontid):
    """ returns zip file with font.ttf and css @font-face snippet 
        all files stored in directory defined in zipdir
    """
    font, fontmeta = db.session.query(Font, FontMeta).\
            filter(and_(Font.id == fontid, Font.name == FontMeta.name)).first()

    font_data = {'font_styles':[(font.as_dict, font.filename)]}
    fontcss = render_template('font_faces.css', **font_data)
    
    font_path = get_font_abs_path(font, fontmeta)

    tmp_file = tempfile.NamedTemporaryFile(suffix='.fonts.tmp')

    with zipfile.ZipFile(tmp_file, mode='w') as zip_tmp:
        # zipdir = font.post_script_name.replace('-', '_')+'/'
        dirname_convention = ''.maketrans({'-':'_', ' ':'_'})
        zipdir = font.post_script_name.translate(dirname_convention)+'/'
        zip_tmp.writestr(zipdir+'fontface.css', bytes(fontcss, encoding='utf-8'))
        add_font_to_zip(font_path, font, zip_tmp, zipdir)
        # Licenses and such need to be included in the zip file
        # txt_paths = [Path(i) for i in Path(font_path).parent.glob('*.txt')]
        txt_paths = [Path(i) for i in 
                     Path(font_path).parent.iterdir() 
                     if i.suffix in('.txt', '.html')]
        [zip_tmp.write(str(i), arcname=zipdir+i.name) for i in txt_paths]

    tmp_file.seek(0)
    att_fn = font.filename.replace('ttf', 'zip')

    return send_file(tmp_file, 
                     as_attachment=True, 
                     attachment_filename=att_fn)
