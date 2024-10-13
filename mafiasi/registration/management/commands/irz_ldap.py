from argparse import ArgumentParser
from pprint import pprint

from django.conf import settings
from django.core.management import BaseCommand

from mafiasi.registration import utils


class Command(BaseCommand):
    help = "Utilities for querying the IRZ ldap"

    def add_arguments(self, parser: ArgumentParser):
        argg = parser.add_mutually_exclusive_group(required=True)
        argg.add_argument("--group", help="Query for a group by gidNumber")
        argg.add_argument("--user", help="Query for a user by uid")

    def handle(self, *args, **options):
        if options["group"] is not None:
            pprint(utils.get_irz_ldap_group(options["group"]))
        elif options["user"] is not None:
            pprint(utils.get_irz_ldap_entry(options["user"]))
        else:
            raise ValueError(f"options contains neither a group nor user parameter: {options}")
