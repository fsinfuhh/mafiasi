import sys
import argparse

from django.conf import settings
from django.core.management.base import BaseCommand
from mafiasi.base.models import PasswdEntry, Mafiasi

class Command(BaseCommand):
    help = 'Loads the passwd file from "getent passwd" into the database'

    def add_arguments(self, parser):
        parser.add_argument('passwd_file', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        passwd_file = options['passwd_file']

        new_entries = 0
        updated_entries = 0
        total_entries = 0
        for lino_no, entry in enumerate(passwd_file):
            total_entries += 1
            entry = entry.strip()
            fields = entry.split(':')
            if len(fields) != 7:
                print('Ignored line {0}. Invalid format'.format(lino_no),
                    file=sys.stderr)
                continue
            
            username = fields[0]
            try:
                gid = int(fields[3])
            except ValueError:
                gid = 0
            full_name = fields[4]
            
            if len(full_name) > 60:
                print('Ignored line {0}. Username too long'.format(lino_no),
                        file=sys.stderr)
                continue

            try:
                passwd_entry = PasswdEntry.objects.get(username=username)
                created = False
            except PasswdEntry.DoesNotExist:
                passwd_entry = PasswdEntry(username=username)
                created = True
                new_entries += 1

            if passwd_entry.gid != gid or passwd_entry.full_name != full_name or created:
                passwd_entry.gid = gid
                passwd_entry.full_name = full_name
                passwd_entry.save()
                updated_entries += 1

        # After importing the new users, unset email addresses of conflicting users
        conflicting_users = Mafiasi.objects.raw("""SELECT base_mafiasi.id FROM base_mafiasi 
            INNER JOIN base_passwdentry ON base_mafiasi.account = base_passwdentry.username
            INNER JOIN base_yeargroup ON base_mafiasi.yeargroup_id = base_yeargroup.id
            WHERE real_email IN
                (SELECT CONCAT(username, '@informatik.uni-hamburg.de') FROM base_passwdentry)
            AND base_yeargroup.gid <> base_passwdentry.gid
            AND base_mafiasi.username SIMILAR TO '\d{2}\w{1,7}'""")

        for user in conflicting_users:
            print(f'Unsetting email address for {user.username}, email was {user.real_email}')
            user.real_email = user.username + '@' + settings.INVALID_MAIL_DOMAIN
            user.save()

        updated_entries -= new_entries # new entries were also updated
        num_in_db = PasswdEntry.objects.count()
        print('{0} new, {1} updated, {2} processed, {3} email addresses unset, {4} in database'.format(
                new_entries, updated_entries, total_entries, len(conflicting_users), num_in_db))
