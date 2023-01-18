from django.conf import settings
from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class BitpollConfig(BaseService):
    default = True
    name = "mafiasi.bitpoll"
    verbose_name = "Bitpoll"
    title = _("BitPoll")
    description = _("BitPoll helps you to find common dates for meetings easily.")
    link = settings.BITPOLL_URL
    image = "img/services/bitpoll.svg"
