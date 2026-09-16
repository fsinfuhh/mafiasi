from dataclasses import dataclass

import ldap
from django.conf import settings
from ldap.dn import str2dn

from mafiasi.utils.ldapmodel import connections


@dataclass(frozen=True)
class LdapRecord:
    dn: str
    attributes: dict[str, list[str]]


def _decode_values(values):
    return [value.decode("utf-8", errors="replace") for value in values]


def _records(base_dn, filterstr, attrs):
    connection = connections["authentik"]
    result = connection.search_s(base_dn, ldap.SCOPE_SUBTREE, filterstr, attrs)
    return [
        LdapRecord(dn, {name: _decode_values(values) for name, values in values.items()})
        for dn, values in result
        if dn
    ]


def users():
    return _records(settings.AUTHENTIK_LDAP_USER_BASE_DN, "(cn=*)", ["cn", "mail", "givenName", "sn"])


def groups():
    return _records(
        settings.AUTHENTIK_LDAP_GROUP_BASE_DN,
        "(cn=*)",
        ["cn", "memberUid", "member", "uniqueMember"],
    )


def first(record, attribute):
    values = record.attributes.get(attribute, [])
    return values[0] if values else ""


def members(record):
    values = []
    for attribute in ("memberUid", "member", "uniqueMember"):
        values.extend(record.attributes.get(attribute, []))

    result = set()
    for value in values:
        if value.lower().startswith(("uid=", "cn=")):
            result.add(str2dn(value)[0][1])
        else:
            result.add(value)
    return result