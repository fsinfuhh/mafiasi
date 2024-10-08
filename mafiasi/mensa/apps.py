from django.conf import settings
from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class MensaConfig(BaseService):
    default = True
    name = "mafiasi.mensa"
    verbose_name = "Mensa"
    title = _("Mensa")
    description = _("Look at what is available in the canteens and filter according to diet, allergens, etc.")
    link = settings.MENSA_URL
    image = "img/services/mensa.svg"
