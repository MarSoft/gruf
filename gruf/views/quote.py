# -*- coding: utf-8 -*-
from flask import Module, g, request, render_template, abort
from gruf.database import Quote

quote = Module(__name__)

@quote.route('/<int:qid>/')
def index(qid):
    quote = Quote.query.get_or_404(qid)
    return render_template('quote.html', quote=quote)

@quote.route('/<int:qid>/rss.xml')
def rss(qid):
    pass

@quote.route('/<int:qid>/edit/', methods=['GET', 'POST'])
def edit(qid):
    if not g.user or not g.user.is_approver(): # только аппрувер может править цитаты
        abort(403, u'У Вас недостаточно прав для выполнения этого действия')
    quote = Quote.query.get_or_404(qid)
    if quote.is_approved() and not g.user.is_admin(): # только админ может менять уже зааппрувленные цитаты
        abort(403)

    if request.method == 'POST':
        pass
