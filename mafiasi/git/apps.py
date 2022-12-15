from django.utils.translation import gettext_lazy as _
from django.conf import settings

from mafiasi.base.base_apps import BaseService


class GitConfig(BaseService):
    name = 'mafiasi.git'
    verbose_name = 'Repositories'
    title = _('Repositories')
    description = _('The Github like repository service')
    link = settings.GIT_URL
    image = 'img/services/git.svg'
