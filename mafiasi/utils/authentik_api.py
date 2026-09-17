from __future__ import annotations

from typing import Any, Iterable

import requests
from django.conf import settings


def get_authentik_api_base_url() -> str:
    base_url = getattr(settings, "AUTHENTIK_API_URL", "")
    return base_url.rstrip("/")


def get_authentik_api_token() -> str:
    return getattr(settings, "AUTHENTIK_API_TOKEN", "") or ""


def _api_session() -> requests.Session:
    session = requests.Session()
    token = get_authentik_api_token()
    if token:
        session.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/json"})
    return session


def _request(method: str, path: str, **kwargs: Any) -> Any:
    base_url = get_authentik_api_base_url()
    if not base_url:
        raise RuntimeError("Authentik API is not configured")

    url = f"{base_url}{path}"
    response = _api_session().request(
        method,
        url,
        timeout=getattr(settings, "AUTHENTIK_API_TIMEOUT", 15),
        **kwargs,
    )

    if response.status_code in {200, 201, 202, 204}:
        if response.content:
            return response.json()
        return None

    raise RuntimeError(f"Authentik API request failed: {response.status_code} {response.text[:200]}")


def build_group_payload(name: str, users: Iterable[int] | None = None, parent: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"name": name}
    if parent:
        parent_group = find_group_by_name(parent)
        if parent_group:
            parent_id = parent_group.get("pk") or parent_group.get("id")
            if parent_id is not None:
                payload["parents"] = [parent_id]
    if users is not None:
        payload["users"] = list(users)
    return payload


def resolve_user_ids(usernames: Iterable[str]) -> list[int]:
    ids: list[int] = []
    for username in usernames:
        if not username:
            continue
        result = _request("GET", "/api/v3/core/users/", params={"username": username})
        if isinstance(result, dict):
            items = result.get("results", [])
        else:
            items = result or []
        for item in items:
            if item.get("username") == username:
                item_id = item.get("pk") or item.get("id")
                if item_id is not None:
                    ids.append(item_id)
                break
    return ids


def find_group_by_name(name: str) -> dict[str, Any] | None:
    result = _request("GET", "/api/v3/core/groups/", params={"search": name})
    if isinstance(result, dict):
        items = result.get("results", [])
    else:
        items = result or []
    for item in items:
        if item.get("name") == name:
            return item
    return None


def create_group(name: str, parent: str | None = None) -> dict[str, Any]:
    payload = build_group_payload(name, parent=parent)
    return _request("POST", "/api/v3/core/groups/", json=payload)


def update_group_membership(group_name: str, usernames: Iterable[str]) -> dict[str, Any] | None:
    group = find_group_by_name(group_name)
    if group is None:
        group = create_group(group_name)

    group_id = group.get("pk") or group.get("id")
    if group_id is None:
        return group

    user_ids = resolve_user_ids(usernames)
    return _request("PATCH", f"/api/v3/core/groups/{group_id}/", json={"users": user_ids})
