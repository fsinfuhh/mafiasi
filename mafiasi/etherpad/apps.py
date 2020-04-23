from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class EtherpadConfig(BaseService):
    name = 'mafiasi.etherpad'
    verbose_name = 'Etherpad'
    title = _('Etherpad')
    description = _('You can use the Etherpad to work together on a document in real time.')
    link = '/etherpad/'
    image = 'img/services/etherpad.png'
