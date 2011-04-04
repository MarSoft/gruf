# -*- coding: utf-8 -*-
from flask import Module, render_template, abort
from sqlalchemy.orm.exc import NoResultFound
from gruf.database import Quote

quote = Module(__name__)

@quote.route('/<qid>/')
def index(qid=None):
    try:
        quote = Quote.query.filter_by(id=qid).one()
    except NoResultFound:
        abort(404)
    return render_template('quote.html', quote=quote)

@quote.route('/<qid>/rss.xml')
def rss(qid=None):
    pass

@quote.route('/<qid>/edit/')
def edit(qid=None):
    pass
