from django.conf import settings
from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class MatrixConfig(BaseService):
    default = True
    name = "mafiasi.matrix"
    verbose_name = "Matrix"
    title = _("Matrix")
    description = _("Matrix provides decentralized messaging and VoIP with E2E encryption.")
    link = settings.MATRIX_URL
    image = "img/services/matrix.svg"
