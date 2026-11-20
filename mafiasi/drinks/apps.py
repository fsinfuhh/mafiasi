from django.conf import settings
from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class DrinksConfig(BaseService):
    default = True
    name = "mafiasi.drinks"
    verbose_name = "Drinks"
    title = _("Drinks")
    description = _("You can use Drinks to buy drinks in the c.t..")
    link = settings.DRINKS_URL
    image = "img/services/drinks.svg"
