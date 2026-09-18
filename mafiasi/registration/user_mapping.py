from typing import Any

from django.conf import settings
from django.contrib.auth.models import Group
from simple_openid_connect.integrations.django.models import OpenidUser
from simple_openid_connect.integrations.django.user_mapping import (
    FederatedUserData,
    UserMapper,
)

from mafiasi.base.models import Mafiasi as MafiasiUser


class MafiasiUserMapper(UserMapper):
    def map_user_attrs(self, user: MafiasiUser, user_data: FederatedUserData) -> None:
        user.username = user_data.username
        user.first_name = user_data.fn or ""
        user.last_name = user_data.sn or ""
        user.email = user_data.email or ""
        user.real_email = user_data.realmail or None

    def sync_group_memberships(self, user: MafiasiUser, groups: list[str]) -> None:
        local_groups = [Group.objects.get_or_create(name=group_name)[0] for group_name in groups if group_name]
        user.groups.set(local_groups)

    def automap_user_attrs(self, user: MafiasiUser, user_data: FederatedUserData) -> None:
        super().automap_user_attrs(user, user_data)
        self.map_user_attrs(user, user_data)
        groups = list(getattr(user_data, "groups", []))
        self.sync_group_memberships(user, groups)
        if settings.OPENID_SYNC_SUPERUSER:
            is_superuser = settings.OPENID_SUPERUSER_GROUP in groups
            user.is_superuser = is_superuser
            user.is_staff = is_superuser

    def handle_federated_userinfo(self, user_data: FederatedUserData) -> MafiasiUser:
        user, created = MafiasiUser.objects.get_or_create(
            username=user_data.username,
            defaults={"account": ""},
        )

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
