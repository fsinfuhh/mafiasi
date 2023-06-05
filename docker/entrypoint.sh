#!/bin/sh
set -e
cd /app/src

echo Compiling locales
pipenv run ./manage.py compilemessages
echo Collecting staticfiles
pipenv run ./manage.py collectstatic --no-input
echo Migrating database
pipenv run ./manage.py migrate
echo Performing system checks
pipenv run ./manage.py check --deploy

echo Executing docker command
exec "$@"
