from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class GitConfig(BaseService):
    name = 'mafiasi.git'
    verbose_name = 'Repositories'
    title = _('Repositories')
    description = _('The Github like repository service')
    link = 'https://git.mafiasi.de'
    image = 'img/services/git.png'
