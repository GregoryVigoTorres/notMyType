from flask import render_template
from flask.ext.security.decorators import login_required

from App.core import admin_bp
# from App.models.admin import AdminModel


@admin_bp.route('/')
@login_required
def index():
    """ Public front page """

    return render_template('index.html')
