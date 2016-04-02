from collections import OrderedDict
from itertools import groupby 
# import logging

from flask import jsonify

from fontTools.ttLib import TTFont

from sqlalchemy import and_

from App.core import (public_bp, db, ub)
from App.models.public import (FontMeta, Font)

from .lib import get_font_css, get_font_abs_path

@public_bp.route('/getspecimen/<int:fontid>')
def get_specimen(fontid):
    """
        gets unicode code blocks and then character categories for each code block
    """
    font, fontmeta = db.session.query(Font, FontMeta).\
            filter(and_(Font.id == fontid, Font.name == FontMeta.name)).\
            first()

    fn = get_font_abs_path(font, fontmeta)
    ttf_font = TTFont(file=fn)

    plat_ids = [i.platformID for i in ttf_font['cmap'].tables]
    if 0 not in plat_ids:
        platform_id = 3 # microsoft
    elif 3 not in plat_ids:
        platform_id = 1 # apple quick draw
    else:
        platform_id = 0 # unicode

    charmap = set()
    for i in ttf_font['cmap'].tables:
        if i.platformID == platform_id:
            charmap.update(i.cmap.items()) 

    # sort charmap by codepoints and filter out . names
    # blocks are determined by codepoint ranges, (see unicode_blocks.json)
    # so the list needs to be sorted by codepoint before grouping
    # ub is unicode blocks
    codepoints_names = sorted([i for i in charmap if not i[1].startswith('.')], key=lambda i: i[0])
    entities = [{'block':ub.get_block(cp),
                 'category':ub.get_cat(cp),
                 'cp':'&#'+str(cp)+';',
                 'name':name} for cp, name in codepoints_names]

    # these are unicode blocks e.g. latin-1
    block_groups = groupby(entities, key=lambda i: i['block'])

    ents_by_block = OrderedDict()
    for k, g in block_groups:
        ents_by_block[k] = list(g)

    # these are character groups, e.g. lowercase letters, within unicode blocks
    # Skip control chracters and spaces
    ent_groups = OrderedDict()
    for k, chars in ents_by_block.items():
        ent_cats = []
        key = lambda i: i['category']
        # list needs to be sorted by same key used for grouping
        for cat, ents in groupby(sorted(chars, key=key), key=key):
            if cat not in ('Control', 'Space Separator'):
                ent_cats.append({'name':cat, 'chars': list(ents)})
        ent_groups[k] = ent_cats 

    fontcss = get_font_css([fontmeta])

    return jsonify({'entities': [{'name':k, 'cats':v} for k, v in ent_groups.items()],
                    'fontdata':font.as_dict,
                    'fontcss':fontcss,
                    'fontmeta':fontmeta.as_dict})
