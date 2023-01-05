from django.utils.translation import gettext_lazy as _
from django.conf import settings

from mafiasi.base.base_apps import BaseService


class WikiConfig(BaseService):
    default = True
    name = 'mafiasi.wiki'
    verbose_name = 'Wiki'
    title = _('Wiki')
    description = _('In the wiki you will find important information regarding your studies.')
    link = settings.WIKI_URL
    image = 'img/services/wiki.svg'
