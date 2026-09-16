from argparse import ArgumentParser

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from mafiasi.base.models import Mafiasi, ldap_import_context
from mafiasi.utils import authentik_ldap


class Command(BaseCommand):
    help = "Synchronize users and groups from the Authentik LDAP outpost"

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--apply", action="store_true", help="Write the LDAP state to the dashboard database")
        parser.add_argument("--users-only", action="store_true")
        parser.add_argument("--groups-only", action="store_true")

    def handle(self, *args, **options):
        if not settings.ENABLE_AUTHENTIK_LDAP_SYNC:
            raise CommandError("Authentik LDAP sync is disabled")
        if options["users_only"] and options["groups_only"]:
            raise CommandError("--users-only and --groups-only cannot be combined")

        ldap_users = [] if options["groups_only"] else authentik_ldap.users()
        ldap_groups = [] if options["users_only"] else authentik_ldap.groups()
        self._validate_unique_keys(ldap_users, "user")
        self._validate_unique_keys(ldap_groups, "group")

        changes = self._changes(ldap_users, ldap_groups)
        self.stdout.write("users: {users}, groups: {groups}, memberships: {memberships}".format(**changes))
        if not options["apply"]:
            self.stdout.write("Dry run; no database changes applied.")
            return

        with transaction.atomic(), ldap_import_context():
            self._apply_users(ldap_users)
            self._apply_groups(ldap_groups)
        self.stdout.write(self.style.SUCCESS("Authentik LDAP state applied."))

    def _validate_unique_keys(self, records, kind):
        keys = [authentik_ldap.first(record, "cn") for record in records]
        if not all(keys):
            raise CommandError("{} LDAP record is missing cn".format(kind.capitalize()))
        if len(keys) != len(set(keys)):
            raise CommandError("Duplicate {} cn in LDAP response".format(kind))

    def _changes(self, ldap_users, ldap_groups):
        user_names = {authentik_ldap.first(record, "cn") for record in ldap_users}
        group_names = {authentik_ldap.first(record, "cn") for record in ldap_groups}
        memberships = sum(len(authentik_ldap.members(record)) for record in ldap_groups)
        return {"users": len(user_names), "groups": len(group_names), "memberships": memberships}

    def _apply_users(self, records):
        for record in records:
            username = authentik_ldap.first(record, "cn")
            defaults = {
                "email": authentik_ldap.first(record, "mail"),
                "first_name": authentik_ldap.first(record, "givenName"),
                "last_name": authentik_ldap.first(record, "sn"),
            }
            user, created = Mafiasi.objects.get_or_create(username=username, defaults={"account": "", **defaults})
            if not created:
                Mafiasi.objects.filter(pk=user.pk).update(**defaults)

    def _apply_groups(self, records):
        for record in records:
            name = authentik_ldap.first(record, "cn")
            group, _created = Group.objects.get_or_create(name=name)
            usernames = authentik_ldap.members(record)
            users = Mafiasi.objects.filter(username__in=usernames)
            group.user_set.set(users)