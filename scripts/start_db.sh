#!/usr/bin/env sh
D=$(realpath $(dirname $0)/..)

mkdir -p "$D/db-data"
exec podman run \
  --rm \
  -e POSTGRES_DB=mafiasi_dashboard \
  -e POSTGRES_USER=mafiasi_dashboard \
  -e POSTGRES_PASSWORD=mafiasi_dashboard \
  -v "$D/db-data:/var/lib/postgresql/data" \
  -p 5432:5432 \
  $@ \
  docker.io/postgres:15
