

import base64
import re
import os

from django.core.management.base import BaseCommand, CommandError
from mafiasi.base.models import Mafiasi
from optparse import make_option

class Command(BaseCommand):
    help = 'Create a guest account'

    def add_arguments(self, parser):
        parser.add_argument('--no-guest',
                            action='store_true',
                            dest='noguest',
                            default=False,
                            help='Do not add .guest to username')
        parser.add_argument('name')
        parser.add_argument('email')
        parser.add_argument('first_name', nargs='?', default=None)
        parser.add_argument('last_name', nargs='?', default=None)

    def handle(self, *args, **options):
        name = options['name']
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']

        if not options['noguest']:
            if not name.endswith('.guest'):
                name += '.guest'

            if not re.match('^[a-z][a-z0-9]*.guest$', name):
                raise CommandError(
                        'Name must be alphanumeric and start with a letter')
        else:  # noguest
            if not re.match('^[a-z0-9\.]*$', name):
                raise CommandError(
                        'Name must be alphanumeric')

        if '@' not in email:
            raise CommandError('Invalid email')

        password = base64.b64encode(os.urandom(15)).lower()
        password = password.replace('/', '').replace('+', '')[:10]

        mafiasi = Mafiasi.objects.create(username=name,
                                         email='{}@cloak.mafiasi.de'.format(name),
                                         real_email=email,
                                         first_name=first_name,
                                         last_name=last_name,
                                         account='')
        mafiasi.set_password(password)
        mafiasi.save()
        print('Created user {} with password {}'.format(name, password))
