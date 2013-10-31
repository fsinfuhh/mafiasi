from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django import template

register = template.Library()

@register.filter(name='format_fingerprint')
def format_fingerprint(fingerprint):
    return u' '.join(fingerprint[i * 4:(i + 1) * 4] for i in xrange(10))

@register.filter(name='show_expires')
def show_expires(subkey):
    if subkey.expires == 0:
        return _('Never.')
    
    expire_date = datetime.fromtimestamp(subkey.expires).strftime('%Y-%m-%d')
    if subkey.expired:
        return _('Expired at {0}').format(expire_date)
    return expire_date

@register.filter(name='show_created')
def show_created(subkey):
    return datetime.fromtimestamp(subkey.timestamp).strftime('%Y-%m-%d')
