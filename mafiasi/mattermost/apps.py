from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class MattermostConfig(BaseService):
    name = 'mafiasi.mattermost'
    verbose_name = 'Mattermost'
    title = _('Chat')
    description = _('An online team chat service')
    link = 'https://mattermost.mafiasi.de/'
    image = 'img/services/mattermost.png'
