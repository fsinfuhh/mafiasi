#!/bin/sh
set -e
cd /app/src

cp -rT /usr/share/javascript/mathjax /app/static/mathjax

./manage.py migrate
mkdir /app/static/django
./manage.py collectstatic --no-input

exec uwsgi /app/config/uwsgi.ini

