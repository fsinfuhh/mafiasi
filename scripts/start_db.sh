#!/usr/bin/env sh
D=$(realpath $(dirname $0)/..)

exec docker run \
  --rm \
  -e POSTGRES_DB=mafiasi-dashboard \
  -e POSTGRES_USER=mafiasi-dashboard \
  -e POSTGRES_PASSWORD=mafiasi-dashboard \
  -v "$D/db-data:/var/lib/postgresql" \
  -p 5432:5432 \
  $@ \
  docker.io/postgres:15
