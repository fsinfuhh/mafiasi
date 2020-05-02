from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class Discourse(BaseService):
    name = 'mafiasi.discourse'
    verbose_name = 'Discourse'
    title = _('Discourse')
    description = _('Discourse is our forum for questions and discussions with your fellow students.')
    link = 'https://discourse.mafiasi.de'
    image = 'img/services/discourse.png'
