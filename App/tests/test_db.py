import pytest

from App.core import db
from App.models.public import Font, FontMeta

@pytest.mark.xfail
def test_font_orphans(client):
    """ There could be FontMeta items with no corresponding Font items """
    fontmeta = db.session.query(FontMeta).all()

    for i in fontmeta:
        assert len(i.fonts)

def test_dupe_fontmeta(client):
    """ names should be unique for fontmeta items """
    fontmeta = db.session.query(FontMeta.name).order_by(FontMeta.name).all()

    for name in fontmeta:
        assert fontmeta.count(name) == 1


def test_dupe_font(client):
    """ post_script_name should be unique for font items """
    fonts = db.session.query(Font.post_script_name).order_by(Font.post_script_name).all()

    for name in fonts:
        assert fonts.count(name) == 1
