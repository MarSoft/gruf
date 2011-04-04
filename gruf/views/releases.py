# -*- coding: utf-8 -*-
from flask import Module

releases = Module(__name__)

@releases.route('/')
def index():
    return 'Hello World!'
