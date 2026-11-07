# auth_fun.py
import json
import secrets
from datetime import UTC, datetime, timedelta

import requests
from django.conf import settings
from django.db import transaction

from mafiasi.guests.models import Invitation

INIVITATION_LIMIT = 10


def check_invite_limit(user) -> dict:
    """Compare a user's invited_users + open_invitations against a fixed limit."""
    user_pk = get_authentik_pk(user.username)
    r = requests.get(f"{_api()}/core/users/{user_pk}/", headers=_headers(), timeout=10)
    r.raise_for_status()
    attributes = r.json().get("attributes") or {}

    invited_count = len(attributes.get("invited_users") or [])
    open_count = len(attributes.get("open_invitations") or [])

    used = invited_count + open_count
    return {
        "invited_users": invited_count,
        "open_invitations": open_count,
        "allowed": used < INIVITATION_LIMIT,
    }


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
    return _user_exists(attributes=json.dumps({"realmail": mail}))


def get_authentik_pk(username: str) -> int:
    r = requests.get(
        f"{_api()}/core/users/",
        headers=_headers(),
        params={"username": username},
        timeout=10,
    )
    r.raise_for_status()
    results = r.json()["results"]
    if len(results) != 1:
        raise LookupError(f"Expected 1 user '{username}', found {len(results)}")
    return results[0]["pk"]


def _api() -> str:
    return settings.AUTHENTIK_API_URL.rstrip("/") + "/api/v3"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.AUTHENTIK_API_TOKEN}"}


def create_invitation(*, inviter_uid: int, username, first_name, last_name, email) -> dict:
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
            "expires": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
            "flow": flow_pk,
            "fixed_data": {
                "username": username,
                "email": email,
                "fn": first_name.strip(),
                "sn": last_name.strip(),
                "invited_by": str(inviter_uid),
            },
        },
    )
    r.raise_for_status()
    invitation = r.json()

    _add_open_invitation(inviter_uid, invitation["pk"])
    return invitation


def _add_open_invitation(username: str, invitation_pk: str) -> None:
    user_pk = get_authentik_pk(username)
    url = f"{_api()}/core/users/{user_pk}/"

    r = requests.get(url, headers=_headers(), timeout=10)
    r.raise_for_status()
    attributes = r.json().get("attributes") or {}

    open_invites = attributes.get("open_invitations", [])
    if invitation_pk not in open_invites:
        open_invites.append(invitation_pk)
    attributes["open_invitations"] = open_invites

    r = requests.patch(url, headers=_headers(), timeout=10, json={"attributes": attributes})
    r.raise_for_status()


def invitation_exists(pk: str) -> bool:
    r = requests.get(f"{_api()}/stages/invitation/invitations/{pk}/", headers=_headers(), timeout=10)
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return True


def delete_invitation(pk: str, username: str) -> bool:
    """True if anything was removed (the invitation, its list entry, or both).
    False if neither existed."""
    rInv = requests.delete(f"{_api()}/stages/invitation/invitations/{pk}/", headers=_headers(), timeout=10)
    invite_deleted = rInv.status_code != 404
    if invite_deleted:
        rInv.raise_for_status()

    user_pk = get_authentik_pk(username)
    user_url = f"{_api()}/core/users/{user_pk}/"
    rUser = requests.get(user_url, headers=_headers(), timeout=10)
    if rUser.status_code == 404:
        return invite_deleted
    rUser.raise_for_status()  # never read attributes from an error response

    attributes = rUser.json().get("attributes") or {}
    open_invites = attributes.get("open_invitations", [])

    in_list = pk in open_invites
    if in_list:
        attributes["open_invitations"] = [i for i in open_invites if i != pk]
        rPatch = requests.patch(user_url, headers=_headers(), timeout=10, json={"attributes": attributes})
        rPatch.raise_for_status()

    return invite_deleted or in_list


def getOpenInvitations(user) -> list[Invitation]:
    user_pk = get_authentik_pk(user)
    rUser = requests.get(f"{_api()}/core/users/{user_pk}/", headers=_headers(), timeout=10)
    rUser.raise_for_status()
    attributes = rUser.json().get("attributes") or {}
    open_ids = attributes.get("open_invitations", [])

    now = datetime.now(UTC)
    valid = {}
    for pk in open_ids:
        r = requests.get(f"{_api()}/stages/invitation/invitations/{pk}/", headers=_headers(), timeout=10)
        if r.status_code == 404:
            continue
        r.raise_for_status()
        inv = r.json()
        expires = inv.get("expires")
        if expires and datetime.fromisoformat(expires) <= now:
            delete_invitation(pk, user)
        valid[str(inv["pk"])] = inv

    ext = settings.GUEST_EXTENSION
    with transaction.atomic():
        Invitation.objects.filter(invited_by=user, authentik_pk__isnull=False).exclude(
            authentik_pk__in=list(valid)
        ).delete()

        for pk, inv in valid.items():
            data = inv.get("fixed_data") or {}
            username = data.get("username", "")
            if ext and username.endswith(ext):
                username = username[: -len(ext)]

            Invitation.objects.filter(invited_by=user, username=username).exclude(authentik_pk=pk).delete()

            Invitation.objects.update_or_create(
                authentik_pk=pk,
                defaults={
                    "username": username,
                    "email": data.get("email", ""),
                    "first_name": data.get("fn", "")[:30],
                    "last_name": (data.get("sn") or data.get("cn", ""))[:30],
                    "invited_by": user,
                },
            )

    return list(Invitation.objects.filter(invited_by=user, authentik_pk__in=list(valid)).order_by("-date_invited"))
