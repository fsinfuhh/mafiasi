from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class MumbleConfig(BaseService):
    name = 'mafiasi.mumble'
    verbose_name = 'Mumble'
    title = _('Mumble')
    description = _('You can use our mumble for voice chat with other fellow students.')
    link = '/mumble/'
    image = 'img/services/mumble.png'
