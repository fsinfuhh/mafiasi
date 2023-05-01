from typing import Any

from django.conf import settings
from simple_openid_connect.data import IdToken

from mafiasi.base.models import Mafiasi as MafiasiUser


def create_user_from_token(id_token: IdToken) -> Any:
    user = MafiasiUser.objects.filter(username=id_token.username)
    assert (
        user.exists()
    ), f"User {id_token.username} does not exist in local database even though users are only ever created from the dashboard"
    user = user.get()
    update_user_from_token(user, id_token)
    return user


def update_user_from_token(user: MafiasiUser, id_token: IdToken) -> None:
    user.email = id_token.email
    user.first_name = id_token.given_name
    user.last_name = id_token.family_name

    if settings.OPENID_SYNC_SUPERUSER:
        user.is_superuser = settings.OPENID_SUPERUSER_GROUP in id_token.groups
