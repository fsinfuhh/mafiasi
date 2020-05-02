from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class WikiConfig(BaseService):
    name = 'mafiasi.wiki'
    verbose_name = 'Wiki'
    title = _('Wiki')
    description = _('In the wiki you will find important information regarding your studies.')
    link = 'https://wiki.mafiasi.de'
    image = 'img/services/wiki.png'
