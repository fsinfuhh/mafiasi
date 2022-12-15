from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class VaultConfig(BaseService):
    default = True
    name = "mafiasi.vault"
    verbose_name = "Vault"
    title = _("Vault")
    description = _("Mafiasi hosted password manager")
    image = "img/services/vaultwarden.png"

    @property
    def link(self):
        return reverse("vault-index")
