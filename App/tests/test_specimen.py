import pytest
from flask import url_for

def test_get_specimen(client):
    resp = client.get(url_for('Public.get_specimen', fontid=100))
    assert resp.status_code == 200

    req_keys = ['fontdata', 'fontmeta', 'entities', 'fontcss']
    for i in req_keys:
        assert resp.json.get(i)
        assert len(resp.json.get(i))
