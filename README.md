# Mafiasi

This is the source code of the django project behind mafiasi.de. This project
is under active development, things may change often.

## Installing

You can install this applications either from source or by building a docker image.

### With Docker

```
docker build -t mafiasi-dashboard .
```


### From Source

To install Mafiasi from source, you need the following apt packages: `libgpgme-dev` and `libgraphviz-dev`

Install the dependencies and start and migrate database:
```
pipenv install
./start_dev_db.sh
pipenv run ./manage.py migrate
```

To run Mafiasi, just start the database and Mafiasi:
```
./start_dev_db.sh
pipenv run ./manage.py runserver
```

# Notes

If you are interested you can see how we deploy this service on our kubernetes cluster via `kustomization.yml`.
The format is [kustomize](https://kustomize.io/).

## Developing

The dashboard application has been modularized and the default development configuration enables only those modules which can function in a local environment (i.e. no LDAP integration).

Once dependencies have been installed (with pipenv), you must start a database with the provided `/scripts/start_db.sh` script.
This will bring up a postgres database that is persistet into the projects repository (but gitignored).

Afterwards, a webserver can be brought up with either of the following commands:

```shell
# directly on your system
./manage.py migrate
./manage.py runserver

# in a podman container
podman build . -t mafiasi-dashboard
podman run -it --net=host -v (realpath .):/app/src/ --env-file .env.dev mafiasi-dashboard /app/src/manage.py runserver
```
