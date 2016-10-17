import pytest
from flask import url_for

def test_download_font(client):
    resp = client.get(url_for('Public.download_font', fontid=100))
    assert resp.status_code == 200
    assert 'attachment; filename=' in resp.headers.get('Content-Disposition')
    assert resp.mimetype == 'application/octet-stream'
    assert len(resp.data)


def test_download_font_family(client):
    resp = client.get(url_for('Public.download_font_family', fontid=49))
    assert resp.status_code == 200
    assert 'attachment; filename=' in resp.headers.get('Content-Disposition')
    assert resp.mimetype == 'application/octet-stream'
    assert len(resp.data)
