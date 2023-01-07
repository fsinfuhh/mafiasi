from typing import Optional

from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from mafiasi.vault.vw_admin import VwUser, VwAdminClient


@method_decorator(login_required, "dispatch")
@method_decorator(csrf_protect, "dispatch")
class IndexView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vw_client = VwAdminClient.init_from_settings()

    def get_vw_user(self) -> Optional[VwUser]:
        """
        Retrieve the vaultwarden user corresponding to the currently logged in mafiasi user from the vaultwarden api
        """
        for user in self.vw_client.list_users():
            if user.email == self.request.user.email:
                return user
        return None

    def get(self, request: HttpRequest) -> HttpResponse:
        vw_user = self.get_vw_user()
        return TemplateResponse(
            request,
            "vault/index.html",
            {
                "vault_account_status": vw_user.status if vw_user else -1,
                "vault_email": request.user.email,
            }
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        if self.get_vw_user() is None:
            self.vw_client.invite_user(request.user.email)
        return HttpResponseRedirect(redirect_to=reverse("vault_index"))
