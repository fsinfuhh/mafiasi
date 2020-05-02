from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class OwncloudConfig(BaseService):
    name = 'mafiasi.owncloud'
    verbose_name = 'Owncloud'
    title = _('Owncloud')
    description = _('OwnCloud enables you to sync and share your documents.')
    link = 'https://cloud.mafiasi.de'
    image = 'img/services/owncloud.png'
