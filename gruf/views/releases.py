# -*- coding: utf-8 -*-
from flask import Module, url_for, flash, render_template, abort, redirect
from gruf.database import Release, db

releases = Module(__name__)

@releases.route('/')
def index():
    releases = Release.query.order_by(Release.version).all()
    return render_template('releases.html', releases=releases)

@releases.route('/create')
def create():
    abort(501)

@releases.route('/<int:ver>/bumped')
def bumped(ver):
    r = Release.query.get_or_404(ver)
    if r.inTree:
        flash(u'Версия #%d уже в дереве!' % ver, 'warning')
    else:
        r.inTree = True
        db.session.commit()
        flash(u'Версия #%d помечена как имеющаяся в дереве. Спасибо за бамп!' % ver, 'info')
    return redirect(url_for('index'))

@releases.route('/<int:ver>/unbump')
def unbump(ver):
    r = Release.query.get_or_404(ver)
    if not r.inTree:
        flash(u'Версия #%d и так не в дереве!' % ver, 'warning')
    else:
        r.inTree = False
        db.session.commit()
        flash(u'Версия #%d помечена как отсутствующая в дереве.' % ver, 'info')
    return redirect(url_for('index'))
