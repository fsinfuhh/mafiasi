from django import template

register = template.Library()

def format_examiners(examiners):
    return ', '.join([e.get_full_name() for e in examiners.all().order_by('last_name')])
register.filter('format_examiners', format_examiners)
