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
    state = db.Column(db.SmallInteger) # 0=Abyss, 1=Approved, 2=Rejected
    STATE_ABYSS = 0
    STATE_APPROVED = 1
    STATE_REJECTED = 2
    text = db.Column(db.Text)
    author = db.Column(db.String(64))
    source = db.Column(db.String(64))
    prooflink = db.Column(db.String(MAX_URI))
    sender_id = db.Column(db.String(64), db.ForeignKey('users.nick'))
    sender = db.relationship('User', backref=db.backref('sent', lazy='dynamic'),
        primaryjoin = 'Quote.sender_id == User.nick')
    approver_id = db.Column(db.String(64), db.ForeignKey('users.nick'))
    approver = db.relationship('User', backref=db.backref('approved', lazy='dynamic'),
        primaryjoin = 'Quote.approver_id == User.nick')
    senddate = db.Column(db.DateTime)
    approvedate = db.Column(db.DateTime)
    offensive = db.Column(db.SmallInteger) # 0=Unknown, 1=Offensive, 2=Good
    OFF_UNKNOWN = 0
    OFF_OFFENSIVE = 1
    OFF_GOOD = 2

    def __init__(self, text, author, source, prooflink, sender,
            senddate = None, approver = None, approvedate = None, offensive = OFF_UNKNOWN, state = STATE_ABYSS):
        self.text = text
        self.author = author
        self.source = source
        self.prooflink = prooflink
        self.sender = sender
        self.approver = approver
        if not senddate:
            datetime.now()
        self.senddate = senddate
        self.approvedate = approvedate
        self.offensive = offensive
        self.state = state

    def is_approved(self):
        return self.state == self.STATE_APPROVED

    def __repr__(self):
        return '<Quote #%s (sent by %s, approved by %s)>' % (self.id, self.sender_id, self.approver_id)

class User(db.Model):
    __tablename__ = 'users'
    nick = db.Column(db.String(64), primary_key = True)
    openid = db.Column(db.String(MAX_URI), unique = True) # None, если не зарегистрирован
    email = db.Column(db.String(128))
    registered = db.Column(db.DateTime)
    rights = db.Column(db.SmallInteger)
    RIGHTS_NORMAL = 0
    RIGHTS_APPROVER = 1
    RIGHTS_RELEASER = 2 # может добавлять релизы
    RIGHTS_ADMIN = 3 # может редактировать других пользователей
    RIGHTS_BANNED = -1
    canComment = db.Column(db.SmallInteger)
    CMT_NORMAL = 0
    CMT_MODERATOR = 1
    CMT_BANNED = -1
    emailConfirmed = db.Column(db.Boolean)
    showOffensiveByDefault = db.Column(db.Boolean) # показывать ли по умолчанию offensive-цитаты

    def __init__(self, nick, email = None, openid = None, rights = RIGHTS_NORMAL, canComment = CMT_NORMAL, registered = None, emailConfirmed = False, showOffensiveByDefault = False):
        self.nick = nick
        self.email = email
        self.openid = openid
        if not registered:
            registered = datetime.now()
        self.registered = registered
        self.rights = rights
        self.canComment = canComment
        self.emailConfirmed = emailConfirmed
        self.showOffensiveByDefault = showOffensiveByDefault

    def __repr__(self):
        return '<User %s (openid %s, rights %i, c_rights %i)' % (self.nick, self.openid, self.rights, self.canComment)

    def can_post(self):
        return not self.rights == self.RIGHTS_BANNED

    def can_comment(self):
        return not self.canComment == self.CMT_BANNED

    def is_approver(self):
        return self.rights in (self.RIGHTS_APPROVER, self.RIGHTS_RELEASER, self.RIGHTS_ADMIN)

    def is_releaser(self):
        return self.rights in (self.RIGHTS_RELEASER, self.RIGHTS_ADMIN)

    def is_admin(self):
        return self.rights == self.RIGHTS_ADMIN

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key = True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    quote = db.relationship('Quote', backref=db.backref('comments', lazy='dynamic'))
    text = db.Column(db.Text)
    sender_id = db.Column(db.String(64), db.ForeignKey('users.nick'))
    sender = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    date = db.Column(db.DateTime)

    def __init__(self, quote, text, sender, date = None):
        self.quote = quote
        self.text = text
        self.sender_id = sender
        if not date:
            date = datetime.now()
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

    def __init__(self, version, count, birthDate = None, inTree = False, isHidden = False):
        self.version = version
        self.count = count
        if not birthDate:
            birthDate = datetime.now()
        self.birthDate = birthDate
        self.inTree = inTree
        self.isHidden = isHidden

    def filename(self, offensive=False):
        """
        Возвращает имя файла.
        @param offensive: если True, то будет возвращено имя файла offensive-цитат для данной версии
        """
        return 'gentoo-ru%s-%d.gz' % (['','-offensive'][offensive], self.version)

    def __repr__(self):
        return '<Release v%i (%i quotes)>' % (self.version, self.count)
