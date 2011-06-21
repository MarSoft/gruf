# -*- coding: utf-8 -*-
from flask import Module

login = Module(__name__)

@login.route('/')
def index():
    return 'Hello World!'

@login.route('/logout')
def logout():
    return 'Hello: logouting?'
