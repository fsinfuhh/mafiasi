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
cp mafiasi/services.py.example mafiasi/services.py
pipenv run ./manage.py migrate
make
```

If you want to use jabber (ejabberd), you have to load the SQL schema
into the database (you'll find it in the ejabberd source code),
migrate the jabber database and do some changes to the tables
```
psql jabber < ejabberd-source-code/sql/pg.sql
./manage.py migrate --database jabber
psql jabber < mafiasi/jabber/sql/*.sql
```

We try to keep these installation instructions up to date, but we can't
guarantee.


# Notes

If you are interested you can see how we deploy this service on our kubernetes cluster via `kustomization.yml`.
The format is [kustomize](https://kustomize.io/). 
