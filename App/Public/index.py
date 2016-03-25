import logging

from flask import (render_template, 
                   request, 
                   jsonify)


from sqlalchemy import (or_, desc)
from sqlalchemy.orm import (contains_eager)

from App.core import (public_bp, db)
from App.models.public import (FontMeta, Font)

from .lib import get_font_css


@public_bp.route('/getfilteredfonts')
def get_filtered_fonts():
    """ fontOptions form 
        accepts json for query params
    """

    # print(request.args)
    page = int(request.args.get('page'))
    limit = int(request.args.get('limit'))
    name_sort = request.args.get('name')
    subsets = request.args.getlist('subset')
    designer_sort = request.args.get('designer')
    weights = request.args.getlist('weight')
    categories = request.args.getlist('category')
    styles = request.args.getlist('style')
    license = request.args.get('license') or ''

    offset = page*limit

    or_weights = [Font.weight == i for i in weights]
    or_styles = [Font.style == i for i in styles]
    sub_subsets = [FontMeta.subsets.contains(i) for i in subsets]
    sub_categories = [FontMeta.category_ref == i for i in categories]

    fq = db.session.query(FontMeta).\
            filter(or_(*sub_subsets)).\
            filter(or_(*sub_categories)).\
            filter(FontMeta.license.like('%'+license)).\
            join(FontMeta.fonts).\
            filter(or_(*or_weights)).\
            filter(or_(*or_styles)).\
            options(contains_eager(FontMeta.fonts))

    font_count = fq.count()
    # before limit/offset

    if name_sort == 'desc':
        fq_ord = fq.order_by(desc(FontMeta.name)).order_by(desc(FontMeta.name))
    elif designer_sort == 'desc':
        fq_ord = fq.order_by(desc(FontMeta.name)).order_by(desc(FontMeta.designer))
    else:
        fq_ord = fq.order_by(FontMeta.name)

    font_objs = fq_ord.offset(offset).limit(limit).all()
    fonts_css = get_font_css(font_objs)
    font_data = [i.as_dict for i in font_objs]
    for i in font_data:
        try:
            i['reg_font_face'] = i['fonts'][0]['post_script_name']
        except Exception as E:
            i['reg_font_face'] = 'Sans-serif'
            logging.debug('get filtered fonts get font face error {}'.format(E))

    fonts_data = {'fontdata':font_data,
                  'fontscss':fonts_css,
                  'fontcount':font_count}

    return jsonify(fonts_data)


@public_bp.route('/getfonts')
def get_fonts():
    """ ajax endpoint 
        return json with font info
        with offset from query params
    """
    page = int(request.args.get('page', 0))
    Limit = 15
    off_set = page * Limit
    letter = request.args.get('letter')
    if letter:
        fq = db.session.query(FontMeta).\
                filter(FontMeta.name.like(letter+'%')).\
                order_by(FontMeta.name)
        font_count = fq.count()
    else:
        fq = db.session.query(FontMeta).order_by(FontMeta.name)
        font_count = fq.count()

    font_objs = fq.offset(off_set).limit(Limit).all()
    fonts_css = get_font_css(font_objs)
    fontdata = [i.as_dict for i in font_objs]
    # get @font-face for each font-family, either *Regular or only font
    for i in fontdata:
        if len(i['fonts']) > 1:
            reg_fams = [j['post_script_name'] for j in i['fonts'] 
                        if 'Regular' in j['post_script_name']]
            if len(reg_fams):
                i['reg_font_face'] = reg_fams[0]
        else:
            try:
                i['reg_font_face'] = i['fonts'][0]['post_script_name']
            except IndexError as E:
                # I don't really know why this happens
                logging.info('get fonts by letter ERROR "{}"'.format(E))
                i['reg_font_face'] = 'Sans-Serif'

    fonts_data = {'fontdata':fontdata,
                  'fontscss':fonts_css,
                  'fontcount':font_count}

    return jsonify(fonts_data)


@public_bp.route('/')
def index():
    """ Public front page 
        this is the base html for the angular app
    """
    return render_template('base.html')
