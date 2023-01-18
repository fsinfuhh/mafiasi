from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from mafiasi.jabber.models import get_or_create_account
from mafiasi.registration.forms import CheckPasswordForm


@login_required
def index(request):
    jabber_user = get_or_create_account(request.user)
    user_display_name = request.user.get_ldapuser().display_name

    return TemplateResponse(
        request,
        "jabber/index.html",
        {
            "jabber_user": jabber_user,
            "user_display_name": user_display_name,
            "jabber_domain": settings.JABBER_DOMAIN,
            "cert_fingerprint": settings.JABBER_CERT_FINGERPRINT,
        },
    )
