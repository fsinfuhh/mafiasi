from urlparse import urlparse

import bleach

def _filter_css_class(name, value):
    if name == 'class':
        if value in ('marker', 'math-tex'):
            return True
    return False

def _build_filter_integer(*attrs):
    def _filter_integer(name, value):
        return name in attrs and value.isdigit()
    return _filter_integer

def _filter_src(name, value):
    if name == 'src':
        p = urlparse(value)
        return p.scheme in ('http', 'https', 'ftp')
    return False

def clean_html(content):
    extra_tags = ['p', 'span', 'h1', 'h2', 'h3', 'pre', 'big', 'small', 'ins',
                  'del', 'table', 'tbody', 'tr', 'td', 'hr']
    allowed_tags = bleach.ALLOWED_TAGS + extra_tags
    allowed_attrs = {
        'span': _filter_css_class,
        'table': _build_filter_integer('border', 'cellpadding', 'cellspacing'),
        'a': _filter_src
    }
    return bleach.clean(content, tags=allowed_tags,
                                 attributes=allowed_attrs)
