from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class BitpollConfig(BaseService):
    name = 'mafiasi.bitpoll'
    verbose_name = 'Bitpoll'
    title = _('BitPoll')
    description = _('BitPoll helps you to find common dates for meetings easily.')
    link = 'https://bitpoll.mafiasi.de'
    image = 'img/services/bitpoll.png'
