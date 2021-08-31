import ldap

from mafiasi import settings
from mafiasi.utils.ldapmodel import connections


def get_irz_ldap_entry(uid):
    connection = connections['registration']
    # Fast search first
    result = settings.REGISTRATION_LDAP_USER_SEARCH_FAST.execute(connection, {'uid': uid})
    if not result:
        # Slow search
        result = settings.REGISTRATION_LDAP_USER_SEARCH_SLOW.execute(connection, {'uid': uid})
        # filter result
        result = [x for x in result if x[0] is not None]
        if not result:
            return None

    result = result[0][1]
    return {
        'name': result['gecos'][0],
        'email': result['mail'][0],
        'uid': uid,
        'gid': result['gidNumber'][0],
    }


def get_irz_ldap_group(gidNumber):
    connection = connections['registration']
    result = settings.REGISTRATION_LDAP_GROUP_SEARCH.execute(connection, {'gidNumber': gidNumber})
    # filter result
    result = [x for x in result if x[0] is not None]
    if not result:
        return None
    return result[0][1]['name'][0]
