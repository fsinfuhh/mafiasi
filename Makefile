base_static = mafiasi/base/static/
dashboard_static = mafiasi/dashboard/static/

all: ${base_static}css/main.min.css ${base_static}css/bootstrap.min.css ${base_static}js/jquery-2.0.3.min.js ${base_static}js/jquery-ui-1.10.3.custom.min.js ${base_static}css/smoothness/jquery-ui-1.10.3.custom.min.css ${dashboard_static}js/dashboard.min.js


%.min.css: %.css
	yui-compressor -o $@ --type css --charset utf-8 $<

%.min.js: %.js
	yui-compressor -o $@ --type js --charset utf-8 $<

clean:
	find -name '*.min.css' -delete
	find -name '*.min.js' -delete
