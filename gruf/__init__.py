# -*- coding: utf-8 -*-

from flask import Flask
from flask import g, session
from flaskext.openid import OpenID

app = Flask(__name__)

import config_default
try:
    import config
except ImportError:
    app.logger.warning('No config.py, using defaults or from envvar!')

app.config.from_object(config_default)
app.config.from_object(config)
app.config.from_envvar('GRUF_CONFIG', silent=True)
oid = OpenID(app)

from gruf.views.main import main
from gruf.views.login import login
from gruf.views.qlist import qlist
from gruf.views.abyss import abyss
from gruf.views.quote import quote
from gruf.views.users import users
from gruf.views.releases import releases
app.register_module(main)
app.register_module(login, url_prefix='/login')
app.register_module(qlist, url_prefix='/list')
app.register_module(abyss, url_prefix='/abyss')
app.register_module(quote, url_prefix='/quote')
app.register_module(users, url_prefix='/users')
app.register_module(releases, url_prefix='/releases')

if not app.debug:
    import logging
    from gruf.logmail import PipeMailHandler
    from gruf.database import User
    mail_handler = PipeMailHandler(User.admin_mails(), 'GRuF: Error')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

@app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        from gruf.database import User
        g.user = User.query.filter_by(openid=session['openid']).first() # first: если нет, то None
