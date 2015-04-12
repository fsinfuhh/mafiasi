from django.apps import AppConfig
from django.conf import settings


class MailinglistConfig(AppConfig):
    name = 'mafiasi.mailinglist'

    def ready(self):
        from mafiasi.mail.signals import collect_servers
        from mafiasi.mailinglist.server import MailinglistServer

        def _attach_server(sender, servers, **kwargs):
            servers.append((MailinglistServer, (settings.MAILINGLIST_SERVER, None)))
        collect_servers.connect(_attach_server, weak=False)
