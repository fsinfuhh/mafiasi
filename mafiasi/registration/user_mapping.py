from typing import Any

from django.conf import settings
from simple_openid_connect.integrations.django.models import OpenidUser
from simple_openid_connect.integrations.django.user_mapping import (
    FederatedUserData,
    UserMapper,
)

from mafiasi.base.models import Mafiasi as MafiasiUser


class MafiasiUserMapper(UserMapper):
    def automap_user_attrs(self, user: MafiasiUser, user_data: FederatedUserData) -> None:
        super().automap_user_attrs(user, user_data)
        if settings.OPENID_SYNC_SUPERUSER:
            groups = getattr(user_data, "groups", [])
            user.is_superuser = settings.OPENID_SUPERUSER_GROUP in groups

    def handle_federated_userinfo(self, user_data: FederatedUserData) -> MafiasiUser:
        # if there is already a user with this username, we create the openid association if it does not exist yet
        try:
            user = MafiasiUser.objects.get(username=user_data.preferred_username)
            OpenidUser.objects.get_or_create(
                sub=user_data.sub,
                defaults={
                    "user": user,
                },
            )
        except MafiasiUser.DoesNotExist:
            # if the user does not exist, it should not be created and and error is raised
            raise AssertionError(
                f"User {user_data.preferred_username} does not exist in local database even though users are only ever created from the dashboard"
            )
        return super().handle_federated_userinfo(user_data)
