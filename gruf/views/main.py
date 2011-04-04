# -*- coding: utf-8 -*-
from flask import Module

main = Module(__name__)

@main.route('/')
def index():
    return 'Hello World!'
