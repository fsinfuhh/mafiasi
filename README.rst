Mafiasi
=======

This is the source code of the django project behind mafiasi.de. This project
is under active development, things may change often.

Dependencies
------------

* Django
* django-widget-tweaks
* nameparser
* creoleparser
* yui-compressor
* gettext

Installation
------------

Just install the dependencies, copy example settings, sync database and
execute make.

::

    pip install -r requirements.txt
    cp mafiasi/settings.py.example mafiasi/settings.py
    ./manage.py syncdb
    make

If you want to use jabber (ejabberd) you have to load the SQL schema
into the database (you'll find it in the ejabberd source code),
sync the jabber database and do some changes to the tables

::

    psql jabber < ejabberd-source-code/sql/pg.sql
    ./manage.py syncdb --database jabber
    psql jabber < mafiasi/jabber/sql/*.sql

We try to keep these installation instructions up to date, but we can't
guarantee.
