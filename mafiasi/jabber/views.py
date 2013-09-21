from django.template.response import TemplateResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

from mafiasi.jabber.models import get_account

def index(request):
    jabber_user = get_account(request.user)

    return TemplateResponse(request, 'jabber/index.html', {
        'jabber_user': jabber_user,
        'jabber_domain': settings.JABBER_DOMAIN,
        'cert_fingerprint': settings.JABBER_CERT_FINGERPRINT
    })

@login_required
def create(request):
    return TemplateResponse(request, 'jabber/create.html', {

    })
