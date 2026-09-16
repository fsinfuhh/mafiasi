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
        user, created = MafiasiUser.objects.get_or_create(
            username=user_data.preferred_username,
            defaults={
                "account": "",
                "email": user_data.email or "",
                "real_email": user_data.email or None,
            },
        )

        if created:
            user.email = user_data.email or ""
            user.real_email = user_data.email or None

        OpenidUser.objects.get_or_create(
            sub=user_data.sub,
            defaults={
                "user": user,
            },
        )

        self.automap_user_attrs(user, user_data)
        user.save()
        return user
