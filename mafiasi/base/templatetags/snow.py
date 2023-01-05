from django.template import Library
from django.utils.timezone import now

register = Library()


@register.simple_tag
def is_snowing():
    n = now()
    return n.month == 12 and n.day >= 10
