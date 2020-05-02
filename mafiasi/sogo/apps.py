from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class SogoConfig(BaseService):
    name = 'mafiasi.sogo'
    verbose_name = 'Calendar'
    title = _('Calendar')
    description = _('Manage and share your calendars and address book, sync them to all your devices.')
    link = 'https://sogo.mafiasi.de'
    image = 'img/services/sogo.png'
