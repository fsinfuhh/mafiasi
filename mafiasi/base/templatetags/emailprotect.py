from django import template
from django.utils.html import conditional_escape, mark_safe

register = template.Library()


@register.filter(name="emailprotect")
def emailprotect(email):
    if "@" not in email:
        return email
    local_part, domain = email.split("@", 1)
    xhtml = '{0}<span class="at-sign"></span>{1}'.format(conditional_escape(local_part), conditional_escape(domain))
    return mark_safe(xhtml)
