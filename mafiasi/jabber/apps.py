from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class JabberConfig(BaseService):
    name = 'mafiasi.jabber'
    verbose_name = 'Jabber'
    title = _('Jabber')
    description = _('On our Jabber server you can chat with your fellow students, which are already on your contact list.')
    link = '/jabber/'
    image = 'img/services/jabber.svg'
