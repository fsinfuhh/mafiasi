static_dir = mafiasi/base/static/

all: ${static_dir}/css/main.min.css ${static_dir}css/bootstrap.min.css ${static_dir}js/jquery-2.0.3.min.js ${static_dir}/js/jquery-ui-1.10.3.custom.min.js


%.min.css: %.css
	yui-compressor -o $@ --type css --charset utf-8 $<

%.min.js: %.js
	yui-compressor -o $@ --type js --charset utf-8 $<

clean:
	$(RM) ${static_dir}/css/*.min.css
	$(RM) ${static_dir}/js/*.min.js
