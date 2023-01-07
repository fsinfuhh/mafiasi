from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from requests import HTTPError

from mafiasi.base.base_apps import BaseService
from mafiasi.vault.vw_admin import VwAdminClient


class VaultConfig(BaseService):
    default = True
    name = "mafiasi.vault"
    verbose_name = "Vault"
    title = _("Vault")
    description = _("Mafiasi hosted password manager")
    image = "img/services/vaultwarden.svg"

    @property
    def link(self):
        return reverse("vault_index")

    def ready(self):
        super().ready()

        # validate vault credentials
        vw_client = VwAdminClient.init_from_settings()
        try:
            vw_client.authenticate()
        except HTTPError as e:
            if e.response.status_code == 401:
                raise ImproperlyConfigured(f"the provided vault admin token is not valid for {vw_client.vw_url}") from e
            raise e
