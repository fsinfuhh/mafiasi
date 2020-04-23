from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class TauschenConfig(BaseService):
    name = 'mafiasi.tauschen'
    verbose_name = 'Mafiasi Tauschen'
    title = _('Mafiasi Tauschen')
    description = _('Mafiasi Tauschen is a service that provides an easy possibility to exchange course groups.')
    link = 'https://tauschen.mafiasi.de'
    image = 'img/services/tauschen.png'
