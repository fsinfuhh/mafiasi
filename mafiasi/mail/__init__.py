from django.conf import settings

from mafiasi.mail.signals import collect_servers

def _attach_server(sender, servers, **kwargs):
    from mafiasi.mail.cloakserver import CloakServer
    servers.append((CloakServer, (settings.MAILCLOAK_SERVER, None)))
collect_servers.connect(_attach_server)
