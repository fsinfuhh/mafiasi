import asyncore
import signal
import sys

from django.core.management.base import NoArgsCommand

from mafiasi.mail.signals import CollectServer, collect_servers

class Command(NoArgsCommand):
    help = 'Starts the SMTP server for mailinglists'

    def handle_noargs(self, *args, **options):
        signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
        servers = []
        collect_servers.send_robust(sender=CollectServer, servers=servers)
        for server_class, server_args in servers:
            server_class(*server_args)
        asyncore.loop()
