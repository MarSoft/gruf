# -*- coding: utf-8 -*-
from flask import Module, render_template, abort
from sqlalchemy.orm.exc import NoResultFound
from gruf.database import User, Quote

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

    new = user.sent.filter_by(state=Quote.STATE_ABYSS)
    accepted = user.sent.filter_by(state=Quote.STATE_APPROVED)
    rejected = user.sent.filter_by(state=Quote.STATE_REJECTED)
    return render_template('profile.html', **locals())
