from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class PksConfig(BaseService):
    name = 'mafiasi.pks'
    verbose_name = 'Keyserver'
    title = _('Keyserver')
    description = _('You can find your fellow students\' OpenPGP keys on our public keyserver.')
    link = '/pks/'
    image = 'img/services/pks.png'
