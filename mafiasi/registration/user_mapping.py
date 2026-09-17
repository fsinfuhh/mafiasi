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
            is_superuser = settings.OPENID_SUPERUSER_GROUP in groups
            user.is_superuser = is_superuser
            user.is_staff = is_superuser

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

        openid_user = OpenidUser.objects.filter(user=user).first()
        if openid_user is None:
            openid_user = OpenidUser.objects.filter(sub=user_data.sub).first()
            if openid_user is not None:
                if openid_user.user_id != user.pk:
                    openid_user.user = user
                    openid_user.save(update_fields=["user"])
            else:
                OpenidUser.objects.create(user=user, sub=user_data.sub)

        self.automap_user_attrs(user, user_data)
        user.save()
        return user
