from django import template

register = template.Library()


def format_examiners(examiners):
    return ", ".join([e.get_full_name() for e in examiners.all().order_by("last_name")])


@register.simple_tag
def is_favorite_filter(favorites, path):
    for favorite in favorites:
        if favorite.url.endswith(path):
            return True
    return False


register.filter("format_examiners", format_examiners)
