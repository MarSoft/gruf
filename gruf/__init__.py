from flask import Flask

app = Flask(__name__)

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
