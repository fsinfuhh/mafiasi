from django.template import Library
from django.utils.timezone import now

register = Library()


@register.simple_tag
def is_first_of_april():
    n = now()
    return n.day == 1 and n.month == 4
