base_static = mafiasi/base/static/
dashboard_static = mafiasi/dashboard/static/

all: css js locales

css: ${base_static}css/main.min.css ${base_static}css/bootstrap.min.css ${base_static}css/smoothness/jquery-ui-1.10.3.custom.min.css

js: ${base_static}js/jquery-2.0.3.min.js ${base_static}js/jquery-ui-1.10.3.custom.min.js ${dashboard_static}js/dashboard.min.js

locales: locale/de_DE/LC_MESSAGES/django.mo locale/en_US/LC_MESSAGES/django.mo

static: css js
	./manage.py collectstatic

%.min.css: %.css
	yui-compressor -o $@ --type css --charset utf-8 $<

%.min.js: %.js
	yui-compressor -o $@ --type js --charset utf-8 $<

%.mo: %.po
	msgfmt -o $@ $<

clean:
	find -name '*.min.css' -delete
	find -name '*.min.js' -delete
	find locale -name '*.mo' -delete
