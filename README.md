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

Just install the dependencies, copy example settings and services, migrate database and
execute make:
```
pipenv install
cp mafiasi/settings.py.example mafiasi/settings.py
pipenv run ./manage.py migrate
make
```

We try to keep these installation instructions up to date, but we can't
guarantee.


# Notes

If you are interested you can see how we deploy this service on our kubernetes cluster via `kustomization.yml`.
The format is [kustomize](https://kustomize.io/).
