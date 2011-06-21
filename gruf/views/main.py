# -*- coding: utf-8 -*-
from flask import Module, render_template

main = Module(__name__)

@main.route('/')
def index():
    return render_template('main.html')
