# -*- coding: utf-8 -*-
from flask import Module, render_template
from gruf.database import db, Quote

quote = Module(__name__)

@quote.route('/<qid>/')
def index(qid=None):
    quote = Quote.query.filter_by(id=qid).one()
    return render_template('quote.html', quote=quote)

@quote.route('/<qid>/rss.xml')
def rss(qid=None):
    pass

@quote.route('/<qid>/edit/')
def edit(qid=None):
    pass
