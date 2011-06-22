# -*- coding: utf-8 -*-
from flask import Module, render_template
from gruf.database import Quote

quote = Module(__name__)

@quote.route('/<int:qid>/')
def index(qid=None):
    quote = Quote.query.get_or_404(qid)
    return render_template('quote.html', quote=quote)

@quote.route('/<int:qid>/rss.xml')
def rss(qid=None):
    pass

@quote.route('/<int:qid>/edit/')
def edit(qid=None):
    pass
