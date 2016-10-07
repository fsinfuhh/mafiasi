import asyncore
import signal
import sys

from django.core.management.base import BaseCommand

from mafiasi.mail.signals import CollectServer, collect_servers

class Command(BaseCommand):
    help = 'Starts the SMTP server for mailinglists'

    def handle(self, *args, **options):
        signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
        servers = []
        collect_servers.send_robust(sender=CollectServer, servers=servers)
        server_instances = []
        for server_class, server_args in servers:
            server_instances.append(server_class(*server_args))
        asyncore.loop()
