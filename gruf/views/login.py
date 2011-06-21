# -*- coding: utf-8 -*-
from flask import Module
from flask import g, session
from gruf.database import User

login = Module(__name__)

@login.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=openid).first()

@login.route('/')
def index():
    return 'Hello World!'

@login.route('/logout')
def logout():
    return 'Hello: logouting?'
