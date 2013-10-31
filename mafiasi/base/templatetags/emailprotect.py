from django.utils.html import mark_safe
from django import template

register = template.Library()

@register.filter(name='emailprotect')
def emailprotect(email):
    local_part, domain = email.split(u'@', 1)
    xhtml = u'{0}<span class="at-sign"></span>{1}'.format(local_part, domain)
    return mark_safe(xhtml)
