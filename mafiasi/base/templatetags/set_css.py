from django import template

register = template.Library()

def set_class(field, css):
    return field.as_widget(attrs={'class': css})

register.filter('set_class', set_class)
