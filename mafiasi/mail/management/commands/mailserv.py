import signal
import threading

from aiosmtpd.controller import Controller
from django.core.management.base import BaseCommand

from mafiasi.mail.signals import CollectServer, collect_servers


class Command(BaseCommand):
    help = "Starts the SMTP server for mailinglists"

    def handle(self, *args, **options):
        servers = []
        collect_servers.send_robust(sender=CollectServer, servers=servers)

        controllers = []
        for handler_class, server_args in servers:
            localaddr = server_args[0]
            controller = Controller(
                handler_class(),
                hostname=localaddr[0],
                port=localaddr[1],
            )
            controller.start()
            controllers.append(controller)

        stop = threading.Event()
        signal.signal(signal.SIGINT, lambda sig, frame: stop.set())
        signal.signal(signal.SIGTERM, lambda sig, frame: stop.set())
        try:
            stop.wait()
        finally:
            for controller in controllers:
                controller.stop()
