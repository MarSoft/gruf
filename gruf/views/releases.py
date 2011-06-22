# -*- coding: utf-8 -*-
from flask import Module, render_template, abort, redirect
from gruf.database import Release

releases = Module(__name__)

@releases.route('/')
def index():
    releases = Release.query.order_by(Release.version).all()
    return render_template('releases.html', **locals())

@releases.route('/create')
def create():
    abort(300)

@releases.route('/<int:ver>/get/')
@releases.route('/<int:ver>/get/<f>')
def get(ver, f=None):
    abourt(300)

@releases.route('/<int:ver>/get-offensive/')
@releases.route('/<int:ver>/get-offensive/<f>')
def get_offensive(ver, f=None):
    abort(300)
