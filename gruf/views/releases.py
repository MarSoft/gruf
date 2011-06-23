# -*- coding: utf-8 -*-
from flask import Module, url_for, flash, Response, render_template, abort, redirect
from gruf.database import Release, Quote, db

releases = Module(__name__)

@releases.route('/')
def index(rss=False):
    releases = Release.query.order_by(Release.version)
    _qq = Quote.query.filter_by(state=Quote.STATE_APPROVED)
    qcount = _qq.filter_by(offensive=Quote.OFF_GOOD).count()
    offencount = _qq.filter_by(offensive=Quote.OFF_OFFENSIVE).count()
    del _qq
    latest = Release.query.order_by(Release.version.desc()).first()

    if rss:
        return Response(render_template('releases.rss.xml', **locals()), mimetype='text/xml')
    else:
        return render_template('releases.html', **locals())

@releases.route('/rss.xml')
def rss():
    return index(rss=True)

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
