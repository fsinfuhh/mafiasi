from django.utils.translation import gettext_lazy as _
from django.conf import settings

from mafiasi.base.base_apps import BaseService


class BitpollConfig(BaseService):
    name = 'mafiasi.bitpoll'
    verbose_name = 'Bitpoll'
    title = _('BitPoll')
    description = _('BitPoll helps you to find common dates for meetings easily.')
    link = settings.BITPOLL_URL
    image = 'img/services/bitpoll.png'
