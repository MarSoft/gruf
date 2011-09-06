# -*- coding: utf-8 -*-
from flask import Module, g, session, request, flash, redirect, render_template
from gruf import oid
from gruf.database import User, db

login = Module(__name__)

@login.route('/', methods=['GET', 'POST'])
@oid.loginhandler
def index():
    if g.user is not None:
        return redirect(oid.get_next_url(), 303)
    if request.method == 'POST':
        if request.form.get('gentoo'):
            openid = 'http://www.gentoo.ru/users/%s/identity' % request.form.get('login')
        else:
            openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['nickname', 'email'])
    return render_template('login.html', next=oid.get_next_url(), error=oid.fetch_error())

@oid.after_login
def do_auth(resp):
    print 'in do_auth'
    session['openid'] = resp.identity_url
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user is None: # регистрируем
        if not resp.nickname:
            return 'Ошибка: не указан ник' # TODO: запросить ник у пользователя. То же для email, если не уникален.
        # а должен ли email быть уникальным?..
        nick = resp.nickname
        n=1
        while User.query.filter_by(nick=nick).count() > 0: # обеспечиваем уникальность ника
            nick = '%s_%d' % (resp.nickname, n)
            n += 1
        user = User(nick, resp.email, openid=resp.identity_url)
        db.session.add(user)
        db.session.commit()
        flash(u'Пользователь зарегистрирован')
    flash(u'Вход выполнен')
    user.update_lastlogin()
    g.user = user
    return redirect(oid.get_next_url(), 303)

@login.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'Вы вышли из системы')
    return redirect(oid.get_next_url(), 303)

