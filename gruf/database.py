# -*- coding: utf-8 -*-
from flaskext.sqlalchemy import SQLAlchemy
from gruf import app
from datetime import datetime

MAX_URI = 256

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
    offensive = db.Column(db.SmallInteger)
    OFF_UNKNOWN = 0
    OFF_OFFENSIVE = 1
    OFF_GOOD = 2
    sentFrom = db.Column(db.SmallInteger)
    SF_WEB = 1
    SF_CLIENT = 2

    def __init__(self, text, author, source, prooflink, sender,
            senddate = None, approver = None, approvedate = None, offensive = OFF_UNKNOWN, state = STATE_ABYSS, sentFrom = SF_WEB):
        self.text = text
        self.author = author
        self.source = source
        self.prooflink = prooflink
        self.sender = sender
        self.approver = approver
        if not senddate:
            senddate = datetime.now()
        self.senddate = senddate
        self.approvedate = approvedate
        self.offensive = offensive
        self.state = state
        self.sentFrom = sentFrom

    def is_abyss(self):
        return self.state == self.STATE_ABYSS
    def is_approved(self):
        return self.state == self.STATE_APPROVED
    def is_rejected(self):
        return self.state == self.STATE_REJECTED

    def is_offensive(self):
        return self.offensive == self.OFF_OFFENSIVE

    def is_fromWeb(self):
        return self.sentFrom == self.SF_WEB
    def is_fromClient(self):
        return self.sentFrom == self.SF_CLIENT

    def __repr__(self):
        return '<Quote #%s (sent by %s, approved by %s)>' % (self.id, self.sender_id, self.approver_id)

class User(db.Model):
    __tablename__ = 'users'
    nick = db.Column(db.String(64), primary_key = True)
    openid = db.Column(db.String(MAX_URI), unique = True) # None, если не зарегистрирован
    email = db.Column(db.String(128))
    registered = db.Column(db.DateTime)
    lastlogin = db.Column(db.DateTime)
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
        self.lastlogin = datetime.now()
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

    def update_lastlogin(self):
        self.lastlogin = datetime.now()
        db.session.commit()

    @staticmethod
    def admin_mails():
        """
        Возвращает все непустые email админов (без дубликатов)
        """
        query = db.session.query(User.email).filter(
                db.and_(User.rights == User.RIGHTS_ADMIN,
                    User.email != None)).distinct()
        return [mail[0] for mail in query]

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
    user = db.relationship('User', backref=db.backref('subscriber', lazy='dynamic'),
            primaryjoin = 'Subscription.user_id == User.nick')
    material = db.Column(db.SmallInteger)
    MT_RELEASES = 1
    MT_COMMENTS = 2
    MT_ABYSS = 3
    MT_QUOTES = 4
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id')) # для MT_COMMENTS; если None, то ко всем цитатам
    quote = db.relationship('Quote', backref=db.backref('subscriptions', lazy='dynamic'))
    offensive = db.Column(db.SmallInteger) # для MT_QUOTES и MT_ABYSS
    OFF_OFFENSIVE = 1 # только оффенсивные
    OFF_GOOD = 2 # только "чистые" (для бездны - неизвестные)
    touser_id = db.Column(db.String(64), db.ForeignKey('users.nick')) # для MT_COMMENTS, MT_ABYSS, MT_QUOTES
    touser = db.relationship('User', backref=db.backref('subscribed', lazy='dynamic'),
            primaryjoin = 'Subscription.touser_id == User.nick')

    def __init__(self, user, material, quote=None, offensive=None):
        self.user = user
        self.material = material
        self.quote = quote
        self.offensive = offensive

    def __repr__(self):
        return '<Subscription of %s to material %i>' % (self.user_id, self.material)

class Release(db.Model):
    __tablename__ = 'releases'
    version = db.Column(db.Integer, primary_key = True)
    count = db.Column(db.Integer) # число хороших цитат
    offencount = db.Column(db.Integer) # число offensive-цитат
    birthDate = db.Column(db.DateTime)
    inTree = db.Column(db.Boolean)
    isHidden = db.Column(db.Boolean)

    def __init__(self, version, count, offencount, birthDate = None, inTree = False, isHidden = False):
        self.version = version
        self.count = count
        self.offencount = offencount
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
