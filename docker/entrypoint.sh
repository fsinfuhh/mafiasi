#!/bin/sh
set -e
cd /app/src

cp -rT /usr/share/javascript/mathjax /app/static/mathjax

./manage.py migrate

exec "$@"
