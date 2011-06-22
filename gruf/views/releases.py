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
