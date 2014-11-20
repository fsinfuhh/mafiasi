from django.conf import settings

from mafiasi.mail.signals import collect_servers
from mafiasi.mail.cloakserver import CloakServer

def _attach_server(sender, servers, **kwargs):
    servers.append((CloakServer, (settings.MAILCLOAK_SERVER, None)))
collect_servers.connect(_attach_server)
