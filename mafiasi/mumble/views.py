from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.conf import settings

def index(request):
    return TemplateResponse(request, 'mumble/index.html', {
        'mumble_domain': settings.MUMBLE_DOMAIN,
        'cert_fingerprint': settings.MUMBLE_CERT_FINGERPRINT
    })
