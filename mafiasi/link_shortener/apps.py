from django.conf import settings
from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class LinkShortenerConfig(BaseService):
    default = True
    name = "mafiasi.link_shortener"
    verbose_name = "Link Shortener"
    title = _("Link Shortener")
    description = _("The best URL shortening service near you")
    link = settings.LINK_SHORTENER_URL
    image = "img/services/link_shortener.svg"
