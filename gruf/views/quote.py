# -*- coding: utf-8 -*-
from flask import Module, g, request, flash, render_template, abort, redirect, url_for
from gruf.database import Quote, User, MAX_URI, db
from wtforms import Form, BooleanField, RadioField, TextField, TextAreaField, validators

quote = Module(__name__)

@quote.route('/<int:qid>/')
def index(qid):
    quote = Quote.query.get_or_404(qid)
    return render_template('quote.html', quote=quote)

@quote.route('/<int:qid>/rss.xml')
def rss(qid):
    pass

class QuoteAddForm(Form):
    text = TextAreaField(u'Текст', [validators.Length(min=3)])
    author = TextField(u'Автор', [validators.Length(min=1, max=64), validators.Optional()])
    source = TextField(u'Источник', [validators.Length(min=2, max=64)])
    prooflink = TextField(u'Пруфлинк', [validators.Length(max=MAX_URI), validators.URL(message=u'Это не похоже на URL!')])
    offensive = BooleanField(u'Оффенсивная')

class QuoteEditForm(QuoteAddForm):
    state = RadioField(u'Статус', choices=[
        (0, u'Бездна'),
        (1, u'Одобрено'),
        (2, u'Свалка (отклонено)'),
        ], coerce=int)
    offensive = RadioField(u'Offensive', choices=[
        (0, u'Неизвестно'),
        (1, u'Да'),
        (2, u'Нет'),
        ], coerce=int)

@quote.route('/add', methods=['GET', 'POST'])
def add():
    if g.user and not g.user.can_post():
        abort(403)
    form = QuoteAddForm(request.form)
    if request.method == 'POST' and form.validate():
        quote = Quote(form.text.data, form.author.data, form.source.data, form.prooflink.data,
                g.user or User.query.get('anonymous'),
                offensive=[Quote.OFF_UNKNOWN, Quote.OFF_OFFENSIVE][form.offensive.data]) # если вкл, то offensive, иначе неизвестно
        db.session.add(quote)
        db.session.commit()
        flash(u'Цитата #%d добавлена' % quote.id, 'info')
        return redirect(url_for('quote.index', qid=quote.id))
    return render_template('quote.edit.html', form=form, quote=None)

@quote.route('/<int:qid>/edit', methods=['GET', 'POST'])
def edit(qid):
    if not g.user or not g.user.is_approver(): # только аппрувер может править цитаты
        abort(403, u'У Вас недостаточно прав для выполнения этого действия')
    quote = Quote.query.get_or_404(qid)
    if quote.is_approved() and not g.user.is_admin(): # только админ может менять уже зааппрувленные цитаты
        abort(403, u'У Вас недостаточно прав для выполнения этого действия')

    form = QuoteEditForm(request.form, quote)
    if request.method == 'POST' and form.validate():
        if g.user.is_admin():
            quote.state = form.state.data
        quote.text = form.text.data
        quote.author = form.author.data
        quote.source = form.source.data
        quote.prooflink = form.prooflink.data
        quote.offensive = form.offensive.data
        db.session.commit()
        flash(u'Цитата #%d отредактирована' % qid, 'info')
        return redirect(url_for('quote.index', qid=qid))
    return render_template('quote.edit.html', quote=quote, form=form) # locals?

@quote.route('/<int:qid>/approve', methods=['GET', 'POST'])
def approve(qid):
    if not g.user or not g.user.is_approver():
        abort(403, u'Вы не можете одобрять цитаты')
    quote = Quote.query.get_or_404(qid)
    if quote.is_approved():
        flash(u'Цитата #%d уже одобрена!' % qid, 'warning')
        return redirect(url_for('quote.index', qid=qid))
    from datetime import datetime
    quote.approver = g.user
    quote.approvedate = datetime.now()
    quote.state = Quote.STATE_APPROVED
    db.session.commit()
    flash(u'Цитата #%d одобрена' % qid, 'info')
    return redirect(url_for('quote.index', qid=qid))

@quote.route('/<int:qid>/delete', methods=['GET', 'POST'])
def delete(qid):
    quote = Quote.query.get_or_404(qid)
    if not g.user:
        abort(403)
    if quote.is_approved():
        if g.user != quote.approver and not g.user.is_admin():
            abort(403, u'Только админ или аппрувер может удалить одобренную цитату')
    else:
        if g.user != quote.sender and not g.user.is_approver():
            abort(403, u'Только аппрувер или отправитель может удалить цитату из бездны')

    db.session.delete(quote)
    db.session.commit()
    flash(u'Цитата #%d удалена' % qid)
    if quote.is_approved():
        return redirect(url_for('qlist.index'))
    else:
        return redirect(url_for('abyss.index'))
