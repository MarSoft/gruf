# -*- coding: utf-8 -*-
from flask import Module, url_for, render_template, abort, redirect
from gruf.database import Release

releases = Module(__name__)

@releases.route('/')
def index():
    releases = Release.query.order_by(Release.version).all()
    return render_template('releases.html', **locals())

@releases.route('/create')
def create():
    abort(501)

@releases.route('/<int:ver>/get/')
@releases.route('/<int:ver>/get/<f>')
def get(ver, f=None):
    r = Release.query.get_or_404(ver)
    if not f:
        return redirect(url_for('get', ver=ver, f=r.filename()), code=301)
    elif f != r.filename():
        abort(404)
    return redirect(url_for('.static', filename='releases/'+r.filename()), code=301)

@releases.route('/<int:ver>/get-offensive/')
@releases.route('/<int:ver>/get-offensive/<f>')
def get_offensive(ver, f=None):
    r = Release.query.get_or_404(ver)
    if not f:
        return redirect(url_for('get_offensive', ver=ver, f=r.filename(offensive=True)), code=301)
    elif f != r.filename(True):
        abort(404)
    return redirect(url_for('.static', filename='releases/'+r.filename(True)), code=301)
