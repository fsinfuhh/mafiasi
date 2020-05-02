#!/bin/sh
set -e
cd /app/src

./manage.py migrate

exec "$@"
