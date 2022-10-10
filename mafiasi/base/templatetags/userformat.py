from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def format_user(user, format='full'):
    ldap_user = user.get_ldapuser()
    nickname = conditional_escape(re.sub(r'(.+)\s\((.+)\)$', r'\1', ldap_user.display_name))
    
    if format == 'full':
        username = conditional_escape(user.username)
        result = '{0} <span class="user-username">({1})</span>'.format(
                nickname, username)
    elif format == 'name':
        result = conditional_escape(nickname)
    elif format == 'username':
        result = conditional_escape(user.username)
    elif format == 'email':
        return '{0} ({1})'.format(nickname, user.username)
    else:
        raise ValueError("Invalid format for format_user")

    return mark_safe(result)
