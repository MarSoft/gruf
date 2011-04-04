# -*- coding: utf-8 -*-
from flask import Module

qlist = Module(__name__)

@qlist.route('/')
def index():
    return 'Hello World!'
