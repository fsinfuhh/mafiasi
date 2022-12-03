#!/bin/sh
set -e
cd /app/src

echo Compiling locales
./manage.py compilemessages
echo Collecting staticfiles
./manage.py collectstatic --no-input
echo Migrating database
./manage.py migrate
echo Performing system checks
./manage.py check --deploy

echo Executing docker command
exec "$@"
