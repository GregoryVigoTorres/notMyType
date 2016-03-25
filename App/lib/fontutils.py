import json
import os.path as osp
import unicodedata

from flask import current_app

class unicodeBlocks():
    def __init__(self):
        """ return unicode block and category for given numeric entity """

        fn = osp.join(osp.dirname(__file__), 'unicode_blocks.json')
        with open(fn) as fd:
            self.uni_block_data = json.load(fd)

        # abbrs for unicode category
        self.unicode_cats = {'Lu':'Uppercase Letter',
                        'Ll':'Lowercase Letter',
                        'Lt':'Titlecase Letter',
                        'Lm':'Modifier Letter',
                        'Lo':'Other Letter',
                        'Mn':'Nonspacing Mark',
                        'Mc':'Spacing Mark',
                        'Me':'Enclosing Mark',
                        'Nd':'Decimal Number',
                        'Nl':'Letter Number',
                        'No':'Other Number',
                        'Pc':'Connector Punctuation',
                        'Pd':'Dash Punctuation',
                        'Ps':'Open Punctuation',
                        'Pe':'Close Punctuation',
                        'Pi':'Initial Punctuation',
                        'Pf':'Final Punctuation',
                        'Po':'Other Punctuation',
                        'Sm':'Math Symbol',
                        'Sc':'Currency Symbol',
                        'Sk':'Modifier Symbol',
                        'So':'Other Symbol',
                        'Zs':'Space Separator',
                        'Zl':'Line Separator',
                        'Zp':'Paragraph Separator',
                        'Cc':'Control',
                        'Cf':'Format',
                        'Cs':'Surrogate',
                        'Co':'Private Use',
                        'Cn':'Unassigned'}


    def get_cat(self, ent):
        """ don't confuse category e.g. punctuation with unicode block e.g. latin-1 """
        cat_abbr = unicodedata.category(chr(ent))
        return self.unicode_cats.get(cat_abbr) or cat_abbr

    def get_block(self, ent):
        """ return unicode block e.g. latin-1 and category name e.g. Math_Symbol """
        for i in self.uni_block_data:
            if ent > i['start'] and ent < i['end']:
                return i['name']
        
        return 'Other'
