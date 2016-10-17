import pytest
from flask import url_for


def test_index(client):
    resp = client.get(url_for('Public.index'))
    assert resp.status_code == 200

def test_get_fonts(client):
    resp = client.get(url_for('Public.get_fonts'))
    assert resp.status_code == 200

def test_paginated_get_fonts(client):
    resp = client.get(url_for('Public.get_fonts', page=2))
    assert resp.status_code == 200
    assert resp.json.get('fontscss')
    assert resp.json.get('fontcount')
    assert resp.json.get('fontdata')

def test_get_fonts_by_letter(client):
    resp = client.get(url_for('Public.get_fonts', page=0, letter='S'))
    assert resp.status_code == 200
    assert resp.json.get('fontscss')
    assert resp.json.get('fontcount')
    assert resp.json.get('fontdata')
    assert len(resp.json.get('fontdata'))
