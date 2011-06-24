# -*- coding: utf-8 -*-
from flask import Module, g, request, flash, render_template, abort, redirect, url_for
from gruf.database import Quote, User, MAX_URI, db
from wtforms import Form, BooleanField, HiddenField, SelectField, RadioField, TextField, TextAreaField, validators

quote = Module(__name__)

class QuoteForm(Form):
    text = TextAreaField(u'Текст', [validators.Length(min=3), validators.Required()])
    author = TextField(u'Автор', [validators.Length(min=1, max=64), validators.Optional()])
    source = TextField(u'Источник', [validators.Length(min=2, max=64), validators.Required()])
    prooflink = TextField(u'Пруфлинк', [validators.Length(max=MAX_URI), validators.URL(message=u'Это не похоже на URL!'), validators.Required()])

class QuoteAddForm(QuoteForm):
    offensive = BooleanField(u'Грубая цитата')
    sender = HiddenField(u'Отправитель', [validators.Length(max=64)]) # ник отправителя, для парсинга запроса bash-клиента
    client = HiddenField(u'Клиент', [validators.NumberRange(min=1, max=2)], filters=([int]), default=Quote.SF_WEB) # FIXME: number range

class QuoteEditForm(QuoteForm):
    state = SelectField(u'Статус', choices=[
        (0, u'Бездна'),
        (1, u'Одобрено'),
        (2, u'Свалка (отклонено)'),
        ], coerce=int)
    offensive = RadioField(u'Грубая цитата', choices=[
        (0, u'Неизвестно'),
        (1, u'Да'),
        (2, u'Нет'),
        ], coerce=int)

@quote.route('/<int:qid>/')
def index(qid):
    quote = Quote.query.get_or_404(qid)
    if quote.is_rejected() and not (g.user and g.user.is_approver()):
        abort(403)
    return render_template('quote.html', quote=quote)

@quote.route('/<int:qid>/rss.xml')
def rss(qid):
    pass

@quote.route('/preview', methods=['GET', 'POST'])
def preview():
    if g.user and not g.user.can_post():
        abort(403)
    abort(501)

@quote.route('/add', methods=['GET', 'POST'])
def add():
    if g.user and not g.user.can_post():
        abort(403)
    form = QuoteAddForm(request.form)
    quote = None
    if request.method == 'POST' and form.validate():
        if form.client.data != Quote.SF_WEB:
            sender = form.sender.data
            user = User.query.get(sender)
            if not user: # не найден
                abort(403, u'Illegal username')
        else:
            user = g.user or User.query.get('anonymous')
        quote = Quote(form.text.data, form.author.data, form.source.data, form.prooflink.data, user,
                offensive=(Quote.OFF_UNKNOWN, Quote.OFF_OFFENSIVE)[form.offensive.data], # если вкл, то offensive, иначе неизвестно
                sentFrom = form.client.data)
        if 'checked' in request.form:
            db.session.add(quote)
            db.session.commit()
            if form.client.data == Quote.SF_WEB:
                flash(u'Цитата #%d добавлена' % quote.id, 'info')
                return redirect(url_for('quote.index', qid=quote.id))
            else:
                return 'Quote %d appended' % quote.id
    if form.client.data != Quote.SF_WEB: # FIXME: client.data может быть битым
        abort(500, u'Bad data.\n'+'\n'.join([e+':'+','.join(form.errors[e]) for e in form.errors]))
    return render_template('quote.edit.html', form=form, preview=quote, quote=None)

@quote.route('/<int:qid>/edit', methods=['GET', 'POST'])
def edit(qid):
    quote = Quote.query.get_or_404(qid)
    if not g.user or (not g.user.is_approver() and g.user != quote.sender): # только аппрувер может править цитаты
        # но отправитель может править свою цитату, пока она в бездне
        abort(403, u'У Вас недостаточно прав для выполнения этого действия')
    if quote.is_approved() and not g.user.is_admin(): # только админ может менять уже зааппрувленные цитаты
        abort(403, u'У Вас недостаточно прав для выполнения этого действия')

    form = QuoteEditForm(request.form, quote)
    if request.method == 'POST' and form.validate():
        if g.user and g.user.is_admin():
            quote.state = form.state.data
        elif form.state.data:
            abort(403) # а то ходют тут всякие, присылают формы левые...
        quote.text = form.text.data
        quote.author = form.author.data
        quote.source = form.source.data
        quote.prooflink = form.prooflink.data
        quote.offensive = form.offensive.data
        if 'checked' in request.form:
            db.session.commit()
            flash(u'Цитата #%d отредактирована' % qid, 'info')
            return redirect(url_for('quote.index', qid=qid))
    return render_template('quote.edit.html', quote=quote, form=form, preview=quote) # locals?

@quote.route('/<int:qid>/approve', methods=['GET', 'POST'])
def approve(qid, reject=False):
    if not g.user or not g.user.is_approver():
        abort(403, u'Вы не можете одобрять или отклонять цитаты')
    quote = Quote.query.get_or_404(qid)
    if quote.is_approved() and not reject:
        flash(u'Цитата #%d уже одобрена!' % qid, 'warning')
        return redirect(url_for('index', qid=qid))
    elif quote.is_rejected() and reject:
        flash(u'Цитата #%d уже отклонена!' % qid, 'warning')
        return redirect(url_for('index', qid=qid))
    if (quote.approver and quote.approver != g.user and
            quote.is_abyss() and not g.user.is_admin()):
        flash(u'Вы не можете менять статус чужой цитаты!', 'error')
        return redirect(url_for('index', qid=qid))
    # FIXME: проверить, указан ли offensive
    # и запросить, если надо
    from datetime import datetime
    quote.approver = g.user
    quote.approvedate = datetime.now()
    quote.state = (Quote.STATE_APPROVED,Quote.STATE_REJECTED)[reject]
    db.session.commit()
    flash(u'Цитата #%d %s' % (qid, (u'одобрена',u'отклонена')[reject]), 'info')
    return redirect(url_for('index', qid=qid))

@quote.route('/<int:qid>/reject', methods=['GET', 'POST'])
def reject(qid):
    return approve(qid, reject=True)

@quote.route('/<int:qid>/delete', methods=['GET', 'POST'])
def delete(qid):
    quote = Quote.query.get_or_404(qid)
    if not g.user:
        abort(403)
    if quote.is_approved():
        if not g.user.is_admin():
            abort(403, u'Вы не можете удалить одобренную цитату')
    else:
        if g.user != quote.sender and not g.user.is_admin():
            abort(403, u'Только отправитель цитаты может удалить её из бездны') # аппрувер может лишь отклонить

    db.session.delete(quote)
    db.session.commit()
    flash(u'Цитата #%d удалена' % qid)
    if quote.is_approved():
        return redirect(url_for('qlist.index'))
    else:
        return redirect(url_for('abyss.index'))
