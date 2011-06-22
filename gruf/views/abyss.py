# -*- coding: utf-8 -*-
from flask import Module
from gruf.views.qlist import display
from gruf.database import Quote

abyss = Module(__name__)

@abyss.route('/')
@abyss.route('/<path:mod>')
def index(mod=None):
    return display(Quote.query.filter_by(
        state=Quote.STATE_ABYSS).all(),
        u'Бездна',
        mod)
