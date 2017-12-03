

from nameparser import HumanName
from django.core.management.base import BaseCommand, CommandError
from mafiasi.base.models import Mafiasi, Yeargroup, PasswdEntry
from mafiasi.jabber.models import JabberUser, SrUser, JabberUserMapping

class Command(BaseCommand):
    def handle(self, *args, **options):
        Mafiasi.objects.all().delete()
        JabberUserMapping.objects.all().delete()
        for jabber_user in JabberUser.objects.all():
            jabber_username = jabber_user.username
            if jabber_username[:2].isdigit():
                self._create_account(jabber_user, jabber_username, jabber_username[1:])
            elif jabber_username[0].isdigit():
                try:
                    year = SrUser.objects.filter(jid=jabber_user.get_jid()).extra(
                        where=["grp LIKE 'j____'"])[0].grp
                    username = year[-2:] + jabber_username[1:]
                    if JabberUser.objects.filter(username=username).count():
                        continue
                    self._create_account(jabber_user, username, jabber_username)
                except IndexError:
                    username = '0' + jabber_username
                    if JabberUser.objects.filter(username=username).count():
                        continue
                    self._create_account(jabber_user, username, jabber_username)
            elif jabber_username.startswith('x'):
                self._create_account(jabber_user, jabber_username, jabber_username)
            else:
                print('Skipping', jabber_username)


    def _create_account(self, jabber_user, username, account):
        try:
            passwd = PasswdEntry.objects.get(username=account)
            name = HumanName(passwd.full_name)
            first_name = name.first
            last_name = name.last
            try:
                yeargroup = Yeargroup.objects.get(gid=passwd.gid)
            except Yeargroup.DoesNotExist:
                yeargroup = None
        except PasswdEntry.DoesNotExist:
            first_name = None
            last_name = None
            yeargroup = None

        if yeargroup is None:
            if username.startswith('x'):
                slug = 'jx'
            else:
                slug = 'j20' + username[:2]
            try:
                yeargroup = Yeargroup.objects.get(slug=slug)
            except Yeargroup.DoesNotExist:
                raise CommandError('No such yeargroup: ' + slug)
                

        mafiasi = Mafiasi(username=username,
                          account=account,
                          yeargroup=yeargroup)
        if first_name and last_name:
            mafiasi.first_name = first_name
            mafiasi.last_name = last_name

        mafiasi.email = account + '@informatik.uni-hamburg.de'

        mafiasi.set_password(jabber_user.password)

        print('Create account', username)
        print(' Account:', account)
        print(' Yeargroup:', yeargroup)
        print(' Name:', mafiasi.first_name, mafiasi.last_name)
        print('--')

        mafiasi.save()
        JabberUserMapping.objects.create(
            mafiasi_user_id=mafiasi.pk,
            jabber_user=jabber_user)
