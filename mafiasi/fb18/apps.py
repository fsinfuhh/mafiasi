from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class Fb18Config(BaseService):
    name = 'mafiasi.fb18'
    verbose_name = 'fb18'
    title = _('FB18')
    description = _('FB18 is our deprecated bulletin board, which is kept here as an archive.')
    link = 'https://archiv.mafiasi.de/forum/fb18/'
    image = 'img/services/fb18.png'
