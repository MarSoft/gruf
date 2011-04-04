# -*- coding: utf-8 -*-
from flask import Module

users = Module(__name__)

@users.route('/')
def index():
    return 'Hello World!'

@users.route('/<nick>/')
def info(nick):
    return 'Userinfo for ' + nick;