import gpgme
from django.conf import settings
from django.core.management.base import BaseCommand
from fuzzywuzzy import fuzz

from mafiasi.base.models import Mafiasi


class Command(BaseCommand):
    help = "Show all OpenPGP keys which do not belong to our community"

    def handle(self, **options):
        self.community_domains = ["@" + domain for domain in settings.PKS_COMMUNITY_DOMAINS]

        full_names = set()
        for mafiasi in Mafiasi.objects.all():
            full_names.add(mafiasi.get_full_name())
        self.full_names = full_names

        ctx = gpgme.Context()
        ctx.keylist_mode = gpgme.KEYLIST_MODE_SIGS
        keys = ctx.keylist()
        foreign_keys = []
        for key in keys:
            if not self.is_community(key):
                foreign_keys.append(key)

        fingerprints = []
        for key in foreign_keys:
            fingerprint = "0x" + key.subkeys[0].fpr
            uid = key.uids[0]
            print("{}: {} <{}>".format(fingerprint, uid.name, uid.email))
            fingerprints.append(fingerprint)

        print("\ngpg --batch --delete-key " + " ".join(fingerprints))

    def is_community(self, key):
        for uid in key.uids:
            if self.is_community_email(uid.email):
                return True
            for sig in uid.signatures:
                if sig.email and self.is_community_email(sig.email):
                    return True
        key_full_name = key.uids[0].name
        for full_name in self.full_names:
            if fuzz.partial_ratio(full_name, key_full_name) > 90:
                return True
        return False

    def is_community_email(self, email):
        email = email.lower()
        return any(email.endswith(domain) for domain in self.community_domains)
