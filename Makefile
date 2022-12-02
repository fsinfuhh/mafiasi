base_static = mafiasi/base/static/
dashboard_static = mafiasi/dashboard/static/
pks_static = mafiasi/pks/static/
mumble_static = mafiasi/mumble/static/
gprot_static = mafiasi/gprot/static/

all: locales

locales:
	./manage.py compilemessages

static:
	./manage.py collectstatic --noinput
