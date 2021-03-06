from django.utils.translation import gettext_lazy as _
from django.conf import settings

from mafiasi.base.base_apps import BaseService


class SogoConfig(BaseService):
    name = 'mafiasi.sogo'
    verbose_name = 'Calendar'
    title = _('Calendar')
    description = _('Manage and share your calendars and address book, sync them to all your devices.')
    link = settings.SOGO_URL
    image = 'img/services/sogo.png'
