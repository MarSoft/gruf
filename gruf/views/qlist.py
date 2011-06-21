# -*- coding: utf-8 -*-
from flask import Module, render_template, abort
from sqlalchemy.orm.exc import NoResultFound
from gruf.database import Quote

qlist = Module(__name__)

# Получает отфильтрованный список цитат и правильно его отображает
def display(quotes, title, mod=None):
    """
    quotes: список объектов-цитат
    title: заголовок страницы (т.е. описание того, что это за набор цитат)
    mod: модификатор (rss.xml, subscribe...), отвечающий за способ вывода или действие
    """
    return render_template('list.html', **locals())

@qlist.route('/')
@qlist.route('/<path:mod>')
def index(mod=None):
    return display(Quote.query.filter_by(
        offensive=Quote.OFF_GOOD, state=Quote.STATE_APPROVED).all(),
        u'Все цитаты',
        mod)

@qlist.route('/sent-by/<nick>')
@qlist.route('/sent-by/<nick>/<path:mod>')
def sent_by(nick, mod=None):
    return display(Quote.query.filter_by(
        sender_id=nick, state=Quote.STATE_APPROVED).all(), # добавить rejected?
        u'Цитаты, присланные пользователем %s' % nick,
        mod)

@qlist.route('/approved-by/<nick>')
@qlist.route('/approved-by/<nick>/<path:mod>')
def approved_by(nick, mod=None):
    return display(Quote.query.filter_by(
        sender_id=nick, state=Quote.STATE_APPROVED).all(),
        u'Цитаты, одобренные пользователем %s' % nick,
        mod)
