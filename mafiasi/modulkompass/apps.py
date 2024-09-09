from django.conf import settings
from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class ModulkompassConfig(BaseService):
    default = True
    name = "mafiasi.modulkompass"
    verbose_name = "Modulkompass"
    title = _("Modulkompass")
    description = _("Share your experiences with courses and look at the experiences of your fellow students.")
    link = settings.MODULKOMPASS_URL
    image = "img/services/modulkompass.svg"
