from django import template
from mafiasi import settings

register = template.Library()

@register.assignment_tag
def settings_value(key):
    return getattr(settings, key, '')

