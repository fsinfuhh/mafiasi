from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class NextcloudConfig(BaseService):
    name = 'mafiasi.nextcloud'
    verbose_name = 'nextcloud'
    title = _('Nextcloud')
    description = _('Nextcloud enables you to sync and share your documents.')
    link = 'https://cloud.mafiasi.de'
    image = 'img/services/nextcloud.png'
