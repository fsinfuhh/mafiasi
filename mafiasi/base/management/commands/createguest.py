from __future__ import print_function, unicode_literals

import base64
import re
import os

from django.core.management.base import BaseCommand, CommandError
from mafiasi.base.models import Mafiasi
from optparse import make_option

class Command(BaseCommand):
    args = '<name> <email> <first_name> <last_name>'
    help = 'Create a guest account'

    option_list = BaseCommand.option_list + (
        make_option('--no-guest',
                        action='store_true',
                        dest='noguest',
                        default=False,
                        help='Do not add .guest to username'),
        )

    def handle(self, *args, **options):
        if len(args) < 3:
            raise CommandError(u'Please provide name and email')
        
        name = args[0]
        email = args[1]
        try:
            first_name = args[2]
        except IndexError:
            first_name = None
        try:
            last_name = args[3]
        except IndexError:
            last_name = None

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

        if u'@' not in email:
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
