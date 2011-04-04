# -*- coding: utf-8 -*-
from flaskext.sqlalchemy import SQLAlchemy
from gruf import app
from datetime import datetime

MAX_URI = 256
# defaults
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/grufortunes.db'

# loading from settings
try:
    from config import SQLALCHEMY_DATABASE_URI
except ImportError:
    print 'Warning: no config'
    app.logger.warning('No settings, will use default DB path!')

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

class Quote(db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key = True)
    rejected = db.Column(db.Boolean)
    text = db.Column(db.Text)
    author = db.Column(db.String(64))
    source = db.Column(db.String(64))
    prooflink = db.Column(db.String(MAX_URI))
    sender_id = db.Column(db.String(64), db.ForeignKey('users.nick'))
    sender = db.relationship('User', backref=db.backref('sent', lazy='dynamic'),
        primaryjoin = 'Quote.sender_id == User.nick')
    approver_id = db.Column(db.String(64), db.ForeignKey('users.nick')) # если None, значит в бездне
    approver = db.relationship('User', backref=db.backref('approved', lazy='dynamic'),
        primaryjoin = 'Quote.approver_id == User.nick')
    senddate = db.Column(db.DateTime)
    approvedate = db.Column(db.DateTime)
    offensive = db.Column(db.SmallInteger) # 0=Unknown, 1=Offensive, 2=Good
    OFF_UNKNOWN = 0
    OFF_OFFENSIVE = 1
    OFF_GOOD = 2

    def __init__(self, text, author, source, prooflink, sender, offensive = OFF_UNKNOWN,
            approver = None, approvedate = None, senddate = datetime.now()):
        self.text = text
        self.author = author
        self.source = source
        self.prooflink = prooflink
        self.sender = sender
        self.approver = approver
        self.senddate = senddate
        self.approvedate = approvedate
        self.offensive = offensive
        self.rejected = False

    def __repr__(self):
        return '<Quote #%s (rej: %s, sent by %s, approved by %s)>' % (self.id, self.rejected, self.sender_id, self.approver_id)

class User(db.Model):
    __tablename__ = 'users'
    nick = db.Column(db.String(64), primary_key = True)
    openid = db.Column(db.String(MAX_URI)) # None, если не зарегистрирован
    registered = db.Column(db.DateTime)
    rights = db.Column(db.SmallInteger) # 0=normal, 1=approver, 2=releaser, 99=banned
    RIGHTS_NORMAL = 0
    RIGHTS_APPROVER = 1
    RIGHTS_RELEASER = 2
    RIGHTS_BANNED = -1
    canComment = db.Column(db.SmallInteger) # 0=normal, 1=moderator, 99=banned
    CMT_NORMAL = 0
    CMT_MODERATOR = 1
    CMT_BANNED = -1
    emailConfirmed = db.Column(db.Boolean)

    def __init__(self, nick, openid = None, rights = RIGHTS_NORMAL, canComment = CMT_NORMAL, registered = datetime.now(), emailConfirmed = False):
        self.nick = nick
        self.openid = openid
        self.registered = registered
        self.rights = rights
        self.canComment = canComment
        self.emailConfirmed = emailConfirmed

    def __repr__(self):
        return '<User %s (openid %s, rights %i, c_rights %i)' % (self.nick, self.openid, self.rights, self.canComment)

    def is_approver(self):
        return self.rights in (self.RIGHTS_APPROVER, self.RIGHTS_RELEASER)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key = True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    quote = db.relationship('Quote', backref=db.backref('comments', lazy='dynamic'))
    text = db.Column(db.Text)
    sender_id = db.Column(db.String(64), db.ForeignKey('users.nick'))
    sender = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    date = db.Column(db.DateTime)

    def __init__(self, quote, text, sender, date = datetime.now()):
        self.quote = quote
        self.text = text
        self.sender_id = sender
        self.date = date

    def __repr__(self):
        return '<Comment %i for %s (by %s)>' % (self.id, self.quote, self.sender_id)

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.nick'))
    user = db.relationship('User', backref=db.backref('subscriptions', lazy='dynamic'))
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    quote = db.relationship('Quote', backref=db.backref('subscriptions', lazy='dynamic'))

    def __init__(self, user, quote):
        self.user = user
        self.quote = quote

    def __repr__(self):
        return '<Subscription of %s to quote %i>' % (self.openid, self.quote)

class Release(db.Model):
    __tablename__ = 'releases'
    version = db.Column(db.Integer, primary_key = True)
    count = db.Column(db.Integer)
    birthDate = db.Column(db.DateTime)
    inTree = db.Column(db.Boolean)
    isHidden = db.Column(db.Boolean)

    def __init__(self, version, count, birthDate = datetime.now(), inTree = False, isHidden = False):
        self.version = version
        self.count = count
        self.birthDate = birthDate
        self.inTree = inTree
        self.isHidden = isHidden

    def __repr__(self):
        return '<Release v%i (%i quotes)>' % (self.version, self.count)
