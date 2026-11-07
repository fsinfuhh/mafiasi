# authentik_checks.py
import secrets
from datetime import datetime, timedelta, timezone

import requests
from django.conf import settings


def _user_exists(**filters) -> bool:
    r = requests.get(
        f"{_api()}/core/users/",
        headers=_headers(),
        params={**filters, "page_size": 1},
        timeout=10,
    )
    r.raise_for_status()
    return len(r.json()["results"]) > 0


def uid_exists(uid: str) -> bool:
    return _user_exists(username=uid)


# Isnt checked for invites, done in auth finally
def mail_exists(mail: str) -> bool:
    return _user_exists(email=mail)


def _api() -> str:
    return settings.AUTHENTIK_API_URL.rstrip("/") + "/api/v3"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.AUTHENTIK_API_TOKEN}"}


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
    base = settings.OPENID_ISSUER.split("/application/")[0]
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
