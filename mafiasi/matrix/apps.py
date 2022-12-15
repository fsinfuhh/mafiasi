from django.utils.translation import gettext_lazy as _
from django.conf import settings

from mafiasi.base.base_apps import BaseService


class MatrixConfig(BaseService):
    name = 'mafiasi.matrix'
    verbose_name = 'Matrix'
    title = _('Matrix')
    description = _('Matrix provides decentralized messaging and VoIP with E2E encryption.')
    link = settings.MATRIX_URL
    image = 'img/services/matrix.svg'
