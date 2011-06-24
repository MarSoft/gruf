#!/bin/bash
# Отправка цитаты на рассмотрение в цитатник сообщества gentoo.ru
# Версия 1.0
#
# Зависимости:
# net-misc/curl
# sys-apps/util-linux
#
# Спасибо haku за идею.

# FIXME при переносе исправить!
SITE='http://marsoft.dyndns.info/gruf/'

preview() {
	echo "Посмотрим, что получилось..."
	echo
	echo "___"
	cat /tmp/cgr-quote.tmp
	echo -e "\t\t-- $author ($source)"
	echo "___"
	echo
	if test -t 0; then # если stdin - терминал
		while :; do
			echo -n "Отправляем? (y/n) "
			read answer
			case "$answer" in
				Y*|y*|Д*|д*)	return;;
				N*|n*|Н*|н*)	exit 0;;
				*)		echo "Ответ непонятен..."
			esac
		done
	else
		echo -n "Отправляем? Если нет, нажмите Ctrl+C в течение 5 секунд"
		for x in `seq 5`; do
			sleep 1
			echo -n ' .'
		done
		echo
	fi
}
send() {
	echo "Отправляю цитату..."
	reply=$(curl \
		--data-urlencode "text@/tmp/cgr-quote.tmp" \
		--data-urlencode "author=$author" \
		--data-urlencode "source=$source" \
		--data-urlencode "prooflink=$prooflink" \
		--data-urlencode "sender=$sender" \
		--data-urlencode "lastname=" \
		--data-urlencode "client=2" \
		--data-urlencode "$offensive" \
		--data-urlencode "checked=on" \
		${SITE}quote/add | tail -1)
	echo
	if qid=$(echo "$reply" | grep 'Quote [0-9]* appended' | grep -o '[0-9]')
	then
		echo "Цитата отправлена успешно!"
		echo "${SITE}quote/$qid"
	else
		echo "Не удалось отправить цитату."
		if [[ "$reply" == "Illegal username" ]]; then
			echo "Неверное имя пользователя. Сначала надо войти хоть раз через веб-интерфейс!"
		else
			echo "$reply"
		fi
	fi
	rm /tmp/cgr-quote.tmp
}
usage() {
	cat <<-END
	Использование:
	 echo цитата | $0 опции
	Опции:
	 -d, --sender: имя отправителя. По умолчанию - текущий логин ($LOGNAME).
	 	Должно совпадать с именем пользователя, зарегистрированного в цитатнике. С учётом регистра.
		Также можно задать через переменную окружения GRUF_USER.
	 -a, --author: автор цитаты. Можно не указывать.
	 -c, --source: источник цитаты. Обязательный параметр. Примеры возможных значений:
	 	gentoo.ru
	 	g@c.g.r
	 	g@c.j.r
	 	awesome@c.g.r
	 	другое
	 -p, --prooflink: ссылка, подтверждающая цитату. Для источников g@c.j.r, g@c.g.r и *@c.g.r
	 	вычисляется автоматически (ставится ссылка на сегодняшние логи), в иных случаях обязательно.
	 -o, --offensive: цитата является грубой/оскорбительной.
	END
	exit 1
}

[ -z "$*" ] && usage

OPTS=$(getopt -o d:a:c:p:oh --long sender,author,source,prooflink,offensive,help -- "$@")

[ $? -eq 0 ] || usage

eval set -- "$OPTS"

[ "$1" == "--" ] && usage

sender="${GRUF_USER}"
while :; do
	case "$1" in
		-d|--sender)	sender="$2"; shift 2;;
		-a|--author)	author="$2"; shift 2;;
		-c|--source)	source="$2"; shift 2;;
		-p|--prooflink)	prooflink="$2"; shift 2;;
		-o|--offensive)	offensive="offensive=on"; shift;;
		-h|--help)	usage;;
		--)		shift; break;;
		*)	echo "Неизвестный аргумент: $1"; exit 1;;
	esac
done

if [ -z "$sender" ]; then
	sender=$LOGNAME
fi
if [ -z "$source" ]; then
	echo "Необходимо указать источник цитаты (source)"
	exit 1
fi
if [ -z "$prooflink" ]; then
	case "$source" in
		g@c.j.r)	prooflink=$(date '+http://chatlogs.jabber.ru/gentoo@conference.jabber.ru/%Y/%m/%d.html');;
		g@c.g.r)	prooflink=$(date '+http://gentoo.ru/jabber/logs/gentoo@conference.gentoo.ru/%Y/%m/%d.html');;
		*@c.g.r)	prooflink=$(date "+http://gentoo.ru/jabber/logs/${source%@c.g.r}@conference.gentoo.ru/%Y/%m/%d.html");;
		*)	echo "Необходимо указать пруфлинк (prooflink)"; exit 1;;
	esac
fi

# Выводим сообщение, если stdin - терминал
test -t 0 && echo "Вводите цитату. Нажмите Ctrl+D, когда закончите..."
# Читаем цитату из stdin. IFS= - чтобы не потерять переводы строки
cat > /tmp/cgr-quote.tmp

if ! [ -s /tmp/cgr-quote.tmp ]; then
	echo "Вы не ввели цитату..."
	exit 1
fi

preview
send

