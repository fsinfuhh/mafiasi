from django.utils.translation import gettext_lazy as _
from django.conf import settings

from mafiasi.base.base_apps import BaseService


class WhiteboardConfig(BaseService):
    name = 'mafiasi.whiteboard'
    verbose_name = 'Whiteboard'
    title = _('Whiteboard')
    description = _('Spacedeck Open is a collaborative whiteboard.')
    link = settings.WHITEBOARD_URL
    image = 'img/services/whiteboard.png'
