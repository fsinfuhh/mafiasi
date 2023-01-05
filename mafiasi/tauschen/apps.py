from django.utils.translation import gettext_lazy as _
from django.conf import settings

from mafiasi.base.base_apps import BaseService


class TauschenConfig(BaseService):
    default = True
    name = 'mafiasi.tauschen'
    verbose_name = 'Mafiasi Tauschen'
    title = _('Mafiasi Tauschen')
    description = _('Mafiasi Tauschen is a service that provides an easy possibility to exchange course groups.')
    link = settings.TAUSCHEN_URL
    image = 'img/services/tauschen.svg'
