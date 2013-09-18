all: mafiasi/base/static/css/bootstrap.min.css

mafiasi/base/static/css/bootstrap.min.css: mafiasi/base/static/css/bootstrap.css
	yui-compressor -o $@ --type css --charset utf-8 $<

clean:
	$(RM) mafiasi/base/static/css/bootstrap.min.css
