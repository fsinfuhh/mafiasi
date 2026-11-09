# auth_fun.py
import json
import logging
import secrets
from datetime import UTC, datetime, timedelta

import requests
from django.conf import settings
from django.db import transaction

from mafiasi.guests.models import Invitation

logger = logging.getLogger(__name__)

INVITATION_LIMIT = 10
INVITATION_VALID_DAYS = 7
TIMEOUT = 10

_session = requests.Session()


def _api() -> str:
    return settings.AUTHENTIK_API_URL.rstrip("/") + "/api/v3"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.AUTHENTIK_API_TOKEN}"}


def _request(method: str, path: str, **kwargs) -> requests.Response:
    """All Authentik calls go through here so headers and timeout are never forgotten."""
    kwargs.setdefault("timeout", TIMEOUT)
    return _session.request(method, f"{_api()}{path}", headers=_headers(), **kwargs)


def _parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def _user_exists(**filters) -> bool:
    r = _request("GET", "/core/users/", params={**filters, "page_size": 1})
    r.raise_for_status()
    return len(r.json()["results"]) > 0


def uid_exists(uid: str) -> bool:
    r = _request(
        "GET",
        "/stages/invitation/invitations/",
        params={"name": uid, "page_size": 1},
    )
    r.raise_for_status()
    results = r.json()["results"]
    if not results:
        return False

    expires = results[0].get("expires")
    return not (expires and _parse_dt(expires) <= datetime.now(UTC)) or _user_exists(username=uid)


# Isn't checked for invites, done in auth finally
def mail_exists(mail: str) -> bool:
    return _user_exists(attributes=json.dumps({"realmail": mail}))


def get_authentik_pk(username: str) -> int:
    r = _request("GET", "/core/users/", params={"username": username})
    r.raise_for_status()
    results = r.json()["results"]
    if len(results) != 1:
        raise LookupError(f"Expected 1 user '{username}', found {len(results)}")
    return results[0]["pk"]


def _get_attributes(user_pk: int) -> dict:
    r = _request("GET", f"/core/users/{user_pk}/")
    r.raise_for_status()
    return r.json().get("attributes") or {}


def _patch_attributes(user_pk: int, attributes: dict) -> None:
    r = _request("PATCH", f"/core/users/{user_pk}/", json={"attributes": attributes})
    r.raise_for_status()


def check_invite_limit(username: str) -> dict:
    attributes = _get_attributes(get_authentik_pk(username))

    invited_count = len(attributes.get("invited_users") or [])
    open_count = len(attributes.get("open_invitations") or [])

    return {
        "invited_users": invited_count,
        "open_invitations": open_count,
        "allowed": invited_count + open_count < INVITATION_LIMIT,
    }


def create_invitation(*, inviter_uid: str, username, first_name, last_name, email) -> dict:
    r = _request("GET", "/flows/instances/guest-enrollment/")
    r.raise_for_status()
    flow_pk = r.json()["pk"]

    slug = username.lower().replace(".", "-")
    r = _request(
        "POST",
        "/stages/invitation/invitations/",
        json={
            "name": f"guest-{slug}-{secrets.token_hex(3)}",
            "single_use": True,
            "expires": (datetime.now(UTC) + timedelta(days=INVITATION_VALID_DAYS)).isoformat(),
            "flow": flow_pk,
            "fixed_data": {
                "username": username,
                "email": username + "@cloak.mafiasi.de",
                "realmail": email,
                "fn": first_name.strip(),
                "sn": last_name.strip(),
                "invited_by": inviter_uid,
            },
        },
    )
    r.raise_for_status()
    invitation = r.json()

    try:
        _add_open_invitation(inviter_uid, invitation["pk"])
    except Exception:
        # don't leave an untracked invitation behind
        try:
            _delete_authentik_invitation(invitation["pk"])
        except requests.RequestException:
            pass
        raise
    return invitation


def _add_open_invitation(username: str, invitation_pk: str) -> None:
    user_pk = get_authentik_pk(username)
    attributes = _get_attributes(user_pk)

    open_invites = list(attributes.get("open_invitations") or [])
    if invitation_pk not in open_invites:
        open_invites.append(invitation_pk)
    attributes["open_invitations"] = open_invites

    _patch_attributes(user_pk, attributes)


def invitation_exists(pk: str) -> bool:
    r = _request("GET", f"/stages/invitation/invitations/{pk}/")
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return True


def _delete_authentik_invitation(pk: str) -> bool:
    """Delete the invitation in Authentik. False if it was already gone (404)."""
    r = _request("DELETE", f"/stages/invitation/invitations/{pk}/")
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return True


def _remove_from_user_open_invitations(pk: str, username: str, user_pk: int | None = None) -> bool:
    if user_pk is None:
        user_pk = get_authentik_pk(username)

    r = _request("GET", f"/core/users/{user_pk}/")
    if r.status_code == 404:
        return False
    r.raise_for_status()

    attributes = r.json().get("attributes") or {}
    open_invites = attributes.get("open_invitations") or []
    if pk not in open_invites:
        return False

    attributes["open_invitations"] = [i for i in open_invites if i != pk]
    _patch_attributes(user_pk, attributes)
    return True


def _delete_local_invitation(pk: str) -> bool:
    Invitation.objects.filter(authentik_pk=pk).delete()
    return True


def delete_invitation(pk: str, username: str, user_pk: int | None = None) -> bool:
    """Best-effort cleanup: runs every step, never raises. True if any step removed something."""
    pk = str(pk)
    steps = (
        ("authentik invitation", lambda: _delete_authentik_invitation(pk)),
        ("user open_invitations", lambda: _remove_from_user_open_invitations(pk, username, user_pk)),
        ("local invitation", lambda: _delete_local_invitation(pk)),
    )

    deleted_any = True
    for name, step in steps:
        try:
            deleted_any |= bool(step())
        except Exception:
            logger.warning("Cleanup step '%s' failed for invitation %s", name, pk, exc_info=True)
    return deleted_any


def get_open_invitations(username: str) -> list[Invitation]:
    user_pk = get_authentik_pk(username)
    open_ids = _get_attributes(user_pk).get("open_invitations") or []

    now = datetime.now(UTC)
    valid = {}

    for pk in open_ids:
        r = _request("GET", f"/stages/invitation/invitations/{pk}/")
        if r.status_code == 404:
            continue
        r.raise_for_status()
        inv = r.json()

        expires = inv.get("expires")
        if expires and _parse_dt(expires) <= now:
            delete_invitation(pk, username, user_pk)
            continue

        valid[str(inv["pk"])] = inv

    with transaction.atomic():
        # delete everything that is not valid in Authentik
        stale = Invitation.objects.filter(invited_by=username).exclude(authentik_pk__in=list(valid))
        stale.delete()

        for pk, inv in valid.items():
            data = inv.get("fixed_data") or {}
            Invitation.objects.update_or_create(
                authentik_pk=pk,
                defaults={
                    "username": data.get("username", ""),
                    "email": data.get("realmail", "")[:100],
                    "first_name": data.get("fn", "")[:30],
                    "last_name": (data.get("sn") or data.get("cn", ""))[:30],
                    "invited_by": username,
                },
            )

    return list(Invitation.objects.filter(invited_by=username, authentik_pk__in=list(valid)).order_by("-date_invited"))


# backwards-compatible alias for existing callers
getOpenInvitations = get_open_invitations
