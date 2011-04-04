# -*- coding: utf-8 -*-
from flask import Module, render_template, abort
from sqlalchemy.orm.exc import NoResultFound
from gruf.database import User

users = Module(__name__)

@users.route('/')
def index():
    return 'Hello World!'

@users.route('/<nick>/')
def profile(nick):
    try:
        user = User.query.filter_by(nick=nick).one()
    except NoResultFound:
        abort(404)
    return render_template('profile.html', user=user)
