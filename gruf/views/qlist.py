# -*- coding: utf-8 -*-
from flask import Module, g, request, render_template, abort
from sqlalchemy.sql import not_
from gruf.database import Quote

qlist = Module(__name__)

# Получает отфильтрованный список цитат и правильно его отображает
def display(quotes, title, mod=None):
    """
    quotes: запрос к таблице цитат
    title: заголовок страницы (т.е. описание того, что это за набор цитат)
    mod: модификатор (rss.xml, subscribe...), отвечающий за способ вывода или действие
    """
    if request.args.has_key('offensive') and request.args['offensive']:
        offense = request.args['offensive']
    else:
        if g.user and g.user.showOffensiveByDefault:
            offense = 'yes'
        else:
            offense = 'no' # незарегистрированным offensive не показываем

    if offense in ['yes', '1', 1]:
        offense = 'yes'
        pass # ничего не фильтруем
    elif offense in ['no', '0', 0]:
        offense = 'no'
        quotes = quotes.filter(not_(Quote.offensive == Quote.OFF_OFFENSIVE))
    elif offense in ['only', '2', 2]:
        offense = 'only'
        quotes = quotes.filter_by(offensive=Quote.OFF_OFFENSIVE)
    else:
        abort(404, u'Неправильное значение переменной offensive=%s' % offense)

    # пагинация

    quotes = quotes.all()
    return render_template('list.html', **locals())

@qlist.route('/')
@qlist.route('/<path:mod>')
def index(mod=None):
    return display(Quote.query.filter_by(
        state=Quote.STATE_APPROVED),
        u'Все цитаты',
        mod)

@qlist.route('/sent-by/<nick>')
@qlist.route('/sent-by/<nick>/<path:mod>')
def sent_by(nick, mod=None):
    return display(Quote.query.filter_by(
        sender_id=nick, state=Quote.STATE_APPROVED), # добавить rejected?
        u'Цитаты, присланные пользователем %s' % nick,
        mod)

@qlist.route('/approved-by/<nick>')
@qlist.route('/approved-by/<nick>/<path:mod>')
def approved_by(nick, mod=None):
    return display(Quote.query.filter_by(
        sender_id=nick, state=Quote.STATE_APPROVED),
        u'Цитаты, одобренные пользователем %s' % nick,
        mod)
