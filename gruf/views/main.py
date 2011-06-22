# -*- coding: utf-8 -*-
from flask import Module, render_template
from gruf.database import Quote, User, Comment, Release

main = Module(__name__)

@main.route('/')
def index():
    quotes = Quote.query
    users = User.query
    comments = Comment.query
    releases = Release.query
    return render_template('main.html', **locals())
