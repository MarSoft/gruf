# -*- coding: utf-8 -*-
from flask import Module, render_template, abort
from gruf.database import User, Quote

users = Module(__name__)

@users.route('/')
def index():
    users = User.query.order_by('nick').all()
    return render_template('userlist.html', **locals())

@users.route('/<nick>')
@users.route('/<nick>/')
def profile(nick):
    user = User.query.get_or_404(nick)
    new = user.sent.filter_by(state=Quote.STATE_ABYSS)
    accepted = user.sent.filter_by(state=Quote.STATE_APPROVED)
    rejected = user.sent.filter_by(state=Quote.STATE_REJECTED)
    return render_template('profile.html', **locals())

@users.route('/<nick>/edit')
def edit(nick):
    abort(501)
