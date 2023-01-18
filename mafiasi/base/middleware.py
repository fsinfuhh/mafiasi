from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from mafiasi.base.models import Mafiasi


class InvalidMailMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if Mafiasi.objects.get(username=request.user.username).real_email.endswith(settings.INVALID_MAIL_DOMAIN):
                messages.error(
                    request,
                    _(
                        "Your email address was automatically set to an invalid one. Please update your email address immediately."
                    ),
                )
        return self.get_response(request)
