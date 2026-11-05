# authentik_checks.py
import secrets
from datetime import datetime, timedelta, timezone

import requests
from django.conf import settings
from ldap3 import SUBTREE, Connection, Server
from ldap3.utils.conv import escape_filter_chars


def _ldap_exists(attr: str, value: str) -> bool:
    server = Server(settings.MAFIASI_LDAP_URI, connect_timeout=5)
    with Connection(
        server,
        user=settings.MAFIASI_LDAP_BIND_DN,
        password=settings.MAFIASI_LDAP_BIND_PW,
        auto_bind=True,
        receive_timeout=10,
    ) as conn:
        conn.search(
            search_base=settings.MAFIASI_LDAP_BASE_DN,
            search_filter=f"(&(objectClass=user)({attr}={escape_filter_chars(value)}))",
            search_scope=SUBTREE,
            attributes=[attr],
            size_limit=1,
        )
        return len(conn.entries) > 0


def uid_exists(uid: str) -> bool:
    return _ldap_exists("uid", uid)


def mail_exists(mail: str) -> bool:
    return _ldap_exists("mail", mail)


def _api() -> str:
    return settings.AUTHENTIK_API_URL.rstrip("/") + "/api/v3"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.MAFIASI_AUTHENTIK_API_TOKEN}"}


def create_invitation(*, username, first_name, last_name, email) -> dict:
    r = requests.get(f"{_api()}/flows/instances/guest-enrollment/", headers=_headers(), timeout=10)
    r.raise_for_status()
    flow_pk = r.json()["pk"]

    slug = username.lower().replace(".", "-")
    r = requests.post(
        f"{_api()}/stages/invitation/invitations/",
        headers=_headers(),
        timeout=10,
        json={
            "name": f"guest-{slug}-{secrets.token_hex(3)}",
            "single_use": True,
            "expires": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "flow": flow_pk,
            "fixed_data": {
                "username": username,
                "email": email,
                "name": f"{first_name} {last_name}".strip(),
            },
        },
    )
    r.raise_for_status()
    return r.json()


def build_invite_link(pk: str) -> str:
    base = settings.MAFIASI_OPENID_ISSUER.split("/application/")[0]
    return f"{base}/if/flow/guest-enrollment/?itoken={pk}"


def invitation_exists(pk: str) -> bool:
    r = requests.get(f"{_api()}/stages/invitation/invitations/{pk}/", headers=_headers(), timeout=10)
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return True


def delete_invitation(pk: str) -> bool:
    """True if deleted, False if it was already gone (used or withdrawn)."""
    r = requests.delete(f"{_api()}/stages/invitation/invitations/{pk}/", headers=_headers(), timeout=10)
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return True
