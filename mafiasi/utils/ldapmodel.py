from copy import deepcopy

import ldap
from ldap.dn import escape_dn_chars
from ldap.modlist import addModlist, modifyModlist
from ldap.ldapobject import ReconnectLDAPObject

from django.conf import settings


class LdapError(Exception):
    pass


class LdapConnectionError(LdapError):
    pass


class LdapNotFound(LdapError):
    pass


class ConnectionManager(object):
    def __init__(self):
        self._connections = {}

    def __getitem__(self, connection_name):
        if connection_name not in self._connections:
            server = settings.LDAP_SERVERS[connection_name]
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, server.get('CA', ''))
            conn = ReconnectLDAPObject(server['URI'])
            conn.simple_bind_s(server['BIND_DN'], server['BIND_PASSWORD'])
            self._connections[connection_name] = conn
        return self._connections[connection_name]

    def __delitem__(self, connection_name):
        if connection_name in self._connections:
            del self._connections[connection_name]


class LdapAttr(object):
    def __init__(self, name, multi=False):
        self.name = name
        self.multi = multi


class LdapList(object):
    def __init__(self, model, list_data):
        self._model = model
        self._list_data = list_data

    def __repr__(self):
        return repr(self._list_data)

    def append(self, item):
        self._model._mark_dirty()
        item = ensure_bytestring(item)
        self._list_data.append(item)

    def remove(self, item):
        self._model._mark_dirty()
        item = ensure_bytestring(item)
        self._list_data.remove(item)

    def __setitem__(self, key, value):
        self._model._mark_dirty()
        value = ensure_bytestring(value)
        self._list_data[key] = value

    def __getitem__(self, key):
        return self._list_data[key].decode('utf-8')

    def __iter__(self):
        for i in range(len(self._list_data)):
            yield self[i]
        

class LdapModelMeta(type):
    def __new__(cls, name, bases, namespace):
        def _make_getter(attr, attr_obj):
            def _get(self):
                if attr_obj.multi:
                    if attr_obj.name not in self._values:
                        self._values[attr_obj.name] = []
                    retval = self._values[attr_obj.name]
                else:
                    try:
                        retval = self._values[attr_obj.name][0]
                    except (IndexError, KeyError):
                        retval = None

                if retval is not None:
                    if attr_obj.multi:
                        retval = LdapList(self, retval)
                    else:
                        retval = retval.decode('utf-8', errors='replace')
                return retval
            return _get
        def _make_setter(attr, attr_obj):
            def _set(self, value):
                self._mark_dirty()
                if value is None:
                    self._values[attr_obj.name] = []
                    return
                value = value.encode('utf-8')

                if attr_obj.multi:
                    if isinstance(value, LdapList):
                        value = value._list_data
                    self._values[attr_obj.name] = value
                else:
                    if attr_obj.name not in self._values:
                        self._values[attr_obj.name] = [None]
                    self._values[attr_obj.name][0] = value
            return _set
        
        for attr, attr_obj in namespace['attrs'].items():
            namespace[attr] = property(_make_getter(attr, attr_obj),
                                       _make_setter(attr, attr_obj))

        class DoesNotExist(LdapNotFound):
            pass

        namespace['DoesNotExist'] = DoesNotExist

        return type.__new__(cls, name, bases, namespace)


class LdapModel(object, metaclass=LdapModelMeta):
    attrs = {}
    object_classes = []
    base_dn = None
    lookup_dn = None
    primary_key = None

    def __init__(self, values=None):
        self._values = {} if values is None else values
        self._old_values = None
        self._fetched = False

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.get_dn())

    def get_dn(self):
        dn_primary = getattr(self, self.primary_key)
        return self.lookup_dn.format(escape_dn_chars(dn_primary))

    def save(self, connection='default', fail_silently=True):
        dn = self.get_dn()
        conn = connections[connection]
        if self._fetched:
            if self._old_values is None:
                # Nothing was changed
                return
            for object_class in self.object_classes:
                if object_class not in self._values['objectClass']:
                    self._values['objectClass'].append(object_class)
            mod_list = modifyModlist(self._old_values, self._values)
            try:
                conn.modify_s(dn, mod_list)
            except ldap.NO_SUCH_OBJECT:
                if not fail_silently:
                    raise

        else:
            self._values['objectClass'] = self.object_classes
            add_list = addModlist(self._values)
            try:
                conn.add_s(dn, add_list)
            except ldap.ALREADY_EXISTS:
                if not fail_silently:
                    raise

    def _mark_dirty(self):
        if self._old_values is None and self._fetched:
            self._old_values = deepcopy(self._values)

    @classmethod
    def lookup(cls, value, connection='default'):
        dn = cls.lookup_dn.format(escape_dn_chars(value))
        conn = connections[connection]
        try:
            result = conn.search_s(dn, ldap.SCOPE_BASE)[0][1]
        except ldap.NO_SUCH_OBJECT:
            raise cls.DoesNotExist(dn)
        instance = cls(result)
        instance._fetched = True
        return instance


def ensure_bytestring(x):
    if isinstance(x, str):
        return x.encode()
    elif isinstance(x, bytes):
        return x
    else:
        return bytes(x)


connections = ConnectionManager()
