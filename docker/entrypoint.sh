#!/bin/sh
set -e
cd /app/src

cp -rT /usr/share/javascript/mathjax /app/static/mathjax

./manage.py migrate
mkdir /app/static/django
./manage.py collectstatic --no-input

if [[ -f "/app/config/uwsgi.ini" ]]; then
  exec uwsgi /app/config/uwsgi.ini
else
  exec uwsgi /app/src/docker/uwsgi.ini
fi
