from django.utils.translation import gettext_lazy as _
from django.conf import settings

from mafiasi.base.base_apps import BaseService


class JitsiConfig(BaseService):
    name = 'mafiasi.jitsi'
    verbose_name = 'Jitsi'
    title = _('Jitsi')
    description = _('Jitsi is a secure and open source video conference tool that can be used in a browser.')
    link = settings.JITSI_URL
    image = 'img/services/jitsi.png'
