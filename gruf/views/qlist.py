# -*- coding: utf-8 -*-
from flask import Module

qlist = Module(__name__)

@qlist.route('/')
def index():
    return 'Hello World!'

@qlist.route('/sent-by/<nick>/')
def sent_by(nick):
    pass

@qlist.route('/approved-by/<nick>/')
def approved_by(nick):
    pass
