# -*- coding: utf-8 -*-
from flask import Module, render_template, abort
from sqlalchemy.orm.exc import NoResultFound
from gruf.database import Quote

qlist = Module(__name__)

# Получает отфильтрованный список цитат и правильно его отображает
def display(quotes, mod):
    pass

@qlist.route('/<path:mod>')
def index(mod):
    return display(Quote.query.filter_by(
        offensive=Quote.OFF_GOOD, state=Quote.STATE_APPROVED).all(),
        mod)

@qlist.route('/sent-by/<nick>/<path:mod>')
def sent_by(nick, mod):
    return display(Quote.query.filter_by(
        sender=nick, state=Quote.STATE_APPROVED).all(), # добавить rejected?
        mod)

@qlist.route('/approved-by/<nick>/<path:mod')
def approved_by(nick, mod):
    return display(Quote.query.filter_by(
        sender=nick, state=Quote.STATE_APPROVED).all(),
        mod)
