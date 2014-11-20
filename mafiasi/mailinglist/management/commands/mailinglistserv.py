import asyncore
import signal
import sys

from django.core.management.base import NoArgsCommand
from django.conf import settings

from mafiasi.mailinglist.server import MailinglistServer

class Command(NoArgsCommand):
    help = 'Starts the SMTP server for mailinglists'

    def handle_noargs(self, *args, **options):
        signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
        MailinglistServer(settings.MAILINGLIST_SERVER, None)
        asyncore.loop()
