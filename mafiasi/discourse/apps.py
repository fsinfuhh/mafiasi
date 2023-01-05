from django.utils.translation import gettext_lazy as _
from django.conf import settings

from mafiasi.base.base_apps import BaseService


class Discourse(BaseService):
    default = True
    name = 'mafiasi.discourse'
    verbose_name = 'Discourse'
    title = _('Discourse')
    description = _('Discourse is our forum for questions and discussions with your fellow students.')
    link = settings.DISCOURSE_URL
    image = 'img/services/discourse.svg'
