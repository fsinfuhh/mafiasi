#!/bin/sh
set -e
cd /app/src

./manage.py compilemessages
./manage.py collectstatic --no-input
./manage.py migrate
./manage.py check --deploy

exec "$@"
