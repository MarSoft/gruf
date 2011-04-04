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

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    nick = db.Column(db.String(64))
    openid = db.Column(db.String(MAX_URI))
    registered = db.Column(db.DateTime)
    rights = db.Column(db.SmallInteger) # 0=normal, 1=approver, 2=releaser, 99=banned
    RIGHTS_NORMAL = 0
    RIGHTS_APPROVER = 1
    RIGHTS_RELEASER = 2
    RIGHTS_BANNED = 99
    canComment = db.Column(db.SmallInteger) # 0=normal, 1=moderator, 99=banned
    CMT_NORMAL = 0
    CMT_MODERATOR = 1
    CMT_BANNED = 99
    emailConfirmed = db.Column(db.Boolean)

#    sent = db.relationship('Quote', backref=db.backref('users', lazy='dynamic'),
#            primaryjoin = id == 'Quote.sender_id')

    def __init__(self, openid, rights = RIGHTS_NORMAL, canComment = CMT_NORMAL, emailConfirmed = False):
        self.openid = openid
        self.rights = rights
        self.canComment = canComment
        self.emailConfirmed = emailConfirmed

    def __repr__(self):
        return '<User #%i, %s (rights %i, c_rights %i)' % (self.id, self.openid, self.rights, self.canComment)

class Quote(db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key = True)
    state = db.Column(db.SmallInteger) # 0=Abyss, 1=Approved, 2=Rejected
    STATE_ABYSS = 0
    STATE_APPROVED = 1
    STATE_REJECTED = 2
    text = db.Column(db.Text)
    author = db.Column(db.String(64))
    source = db.Column(db.String(64))
    prooflink = db.Column(db.String(MAX_URI))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender = db.relationship('User', backref=db.backref('quotes', lazy='dynamic'),
        primaryjoin = sender_id == User.id)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approver = db.relationship('User', backref=db.backref('quotes.approver_id', lazy='dynamic'),
        primaryjoin = approver_id == User.id)
    senddate = db.Column(db.DateTime)
    approvedate = db.Column(db.DateTime)
    offensive = db.Column(db.SmallInteger) # 0=Unknown, 1=Offensive, 2=Good
    OFF_UNKNOWN = 0
    OFF_OFFENSIVE = 1
    OFF_GOOD = 2

    def __init__(self, text, author, source, prooflink, sender,
            senddate = datetime.now(), approver = None, approvedate = None, offensive = OFF_UNKNOWN, state = STATE_ABYSS):
        self.text = text
        self.author = author
        self.source = source
        self.prooflink = prooflink
        self.sender = sender
        self.approver_id = approver
        self.senddate = senddate
        self.approvedate = approvedate
        self.offensive = offensive
        self.state = state

    def __repr__(self):
        return '<Quote %s (state %i, sent by %s, approved by %s)>' % (self.id, self.state, self.sender, self.approver_id)

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

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key = True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    quote = db.relationship('Quote', backref=db.backref('comments', lazy='dynamic'))
    text = db.Column(db.Text)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    date = db.Column(db.DateTime)

    def __init__(self, quote, text, sender, date = datetime.now()):
        self.quote_id = quote
        self.text = text
        self.sender_id = sender
        self.date = date

    def __repr__(self):
        return '<Comment %i for %i (by %s)>' % (self.id, self.quoteid, self.sender)

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('subscriptions', lazy='dynamic'))
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    quote = db.relationship('Quote', backref=db.backref('subscriptions', lazy='dynamic'))

    def __init__(self, user, quote):
        self.user_id = user
        self.quote_id = quote

    def __repr__(self):
        return '<Subscription of %s to quote %i>' % (self.openid, self.quote)
