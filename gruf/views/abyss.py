# -*- coding: utf-8 -*-
from flask import Module

abyss = Module(__name__)

@abyss.route('/')
def index():
    return 'Hello World!'
