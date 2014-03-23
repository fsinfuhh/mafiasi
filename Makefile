base_static = mafiasi/base/static/
dashboard_static = mafiasi/dashboard/static/
cal_static = mafiasi/cal/static/
pks_static = mafiasi/pks/static/
mumble_static = mafiasi/mumble/static/
gprot_static = mafiasi/gprot/static/
mathjax_version = 2.3
mathjax_static = ${base_static}MathJax-${mathjax_version}/

all: css js locales mathjax

css: ${base_static}css/main.min.css ${base_static}css/bootstrap.min.css ${base_static}css/smoothness/jquery-ui-1.10.3.custom.min.css ${cal_static}css/fullcalendar.min.css ${cal_static}css/cal.min.css ${pks_static}css/pks.min.css ${mumble_static}css/mumble.min.css

js: ${base_static}js/jquery-2.0.3.min.js ${base_static}js/jquery-ui-1.10.3.custom.min.js ${base_static}js/common.min.js ${base_static}js/autocomplete.min.js ${dashboard_static}js/dashboard.min.js ${cal_static}js/fullcalendar.min.js ${pks_static}js/pks-graph.min.js ${gprot_static}js/gprot.min.js

locales: locale/de_DE/LC_MESSAGES/django.mo locale/en_US/LC_MESSAGES/django.mo

mathjax: ${mathjax_static}MathJax.js ${mathjax_static}jax ${mathjax_static}config ${mathjax_static}localization ${mathjax_static}extensions ${mathjax_static}fonts ${base_static}mathjax

${base_static}mathjax: ${mathjax_static}
	ln -s ${<:${base_static}%=%} $@

${mathjax_static}%: /tmp/MathJax-${mathjax_version}.tar.gz
	tar -C ${base_static} -xzf $< ${@:${base_static}%=%}
	touch $@

/tmp/MathJax-${mathjax_version}.tar.gz:
	wget https://github.com/mathjax/MathJax/archive/v${mathjax_version}.tar.gz -O $@

static: css js
	./manage.py collectstatic --noinput

%.min.css: %.css
	yui-compressor -o $@ --type css --charset utf-8 $<

%.min.js: %.js
	yui-compressor -o $@ --type js --charset utf-8 $<

%.mo: %.po
	msgfmt -o $@ $<

clean: cleanmathjax
	find -name '*.min.css' -delete
	find -name '*.min.js' -delete
	find locale -name '*.mo' -delete

cleanmathjax:
	rm -rf ${mathjax_static}
	rm -f ${base_static}mathjax
	rm -rf /tmp/MathJax-${mathjax_version}.tar.gz
