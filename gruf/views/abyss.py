# -*- coding: utf-8 -*-
from flask import Module, g, abort
from gruf.views.qlist import display
from gruf.database import Quote

abyss = Module(__name__)

@abyss.route('/')
@abyss.route('/<path:mod>')
def index(mod=None):
    return display(Quote.query.filter_by(
        state=Quote.STATE_ABYSS),
        u'Бездна',
        mod, abyss=True)

@abyss.route('/trash/')
@abyss.route('/trash/<path:mod>')
def trash(mod=None):
    if not g.user or not g.user.is_approver():
        abort(403)
    return display(Quote.query.filter_by(
        state=Quote.STATE_REJECTED),
        u'Кладбище цитат',
        mod, abyss=True)
