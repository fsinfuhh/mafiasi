from argparse import ArgumentParser

from django.conf import settings
from django.core.management import BaseCommand

from mafiasi.base.models import Mafiasi as MafiasiUser


class Command(BaseCommand):
    help = "Create a user for development in the local database"

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("username", type=str)

    def handle(self, *args, **options):
        username = options["username"]
        MafiasiUser.objects.create_superuser(
            username=username, email="email@localhost", password=None, real_email="real_email@localhost"
        )

        print(f"Created local superuser {username} for development")
        if settings.OPENID_SYNC_SUPERUSER:
            print(
                f"Warning: The superuser status will be overwritten when you log in because MAFIASI_OPENID_SYNC_SUPERUSER is on and configured to be based on the group '{settings.OPENID_SUPERUSER_GROUP}'"
            )
