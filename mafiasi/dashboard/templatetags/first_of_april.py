from django.utils.timezone import now
from django.template import Library

register = Library()


@register.simple_tag
def is_first_of_april():
    n = now()
    return n.day == 1 and n.month == 4
