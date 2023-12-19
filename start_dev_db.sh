#!/usr/bin/bash
set -e

export USER=mafiasi_dashboard
export PASS=$USER
export DB=$USER
export STORE_DIR=$(realpath $(dirname $(dirname $0)))/dev_db

mkdir -p $STORE_DIR
echo "Exposing postgres database on psql://$USER:$PASS@localhost:5432/$DB"
exec docker run \
    -it \
    -e POSTGRES_USER=$USER \
    -e POSTGRES_PASSWORD=$PASS \
    -e POSTGRES_DB=$DB \
    -v $STORE_DIR:/var/lib/postgresql/data \
    -p 5432:5432 \
    $@ \
    docker.io/postgres