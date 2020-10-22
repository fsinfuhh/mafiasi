from django.utils.translation import gettext_lazy as _
from django.conf import settings

from mafiasi.base.base_apps import BaseService


class KanboardConfig(BaseService):
    name = 'mafiasi.kanboard'
    verbose_name = 'Kanboard'
    title = _('Kanboard')
    description = _('Kanboard is a kanban project management tool that you can use to track the progress of your projects.')
    link = settings.KANBOARD_URL
    image = 'img/services/kanboard.png'
