from django.conf import settings
from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class OverleafConfig(BaseService):
    default = True
    name = "mafiasi.overleaf"
    verbose_name = "Overleaf"
    title = _("Overleaf")
    description = _("Overleaf is a collaborative LaTeX editor, with features from the premium version.")
    link = settings.OVERLEAF_URL
    image = "img/services/overleaf.svg"
