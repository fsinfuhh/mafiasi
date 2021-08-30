import ldap

from mafiasi import settings

_irz_ldap = None


def _get_irz_ldap():
    global _irz_ldap
    if _irz_ldap is None:
        # Before starting the connection, the custom CA certificate must be added
        ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, settings.REGISTRATION_LDAP_CA)
        _irz_ldap = ldap.initialize(settings.REGISTRATION_LDAP_URI)
        _irz_ldap.simple_bind_s(settings.REGISTRATION_LDAP_BIND_DN, settings.REGISTRATION_LDAP_PASSWORD)
    return _irz_ldap


def get_irz_ldap_entry(uid):
    connection = _get_irz_ldap()
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
    connection = _get_irz_ldap()
    result = settings.REGISTRATION_LDAP_GROUP_SEARCH.execute(connection, {'gidNumber': gidNumber})
    # filter result
    result = [x for x in result if x[0] is not None]
    if not result:
        return None
    return result[0][1]['name'][0]
