from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

def index(request):
    config = {
        'label': _('Student association'),
    }
    config.update(settings.MUMBLE_SERVER)
    return TemplateResponse(request, 'mumble/index.html', {
        'config': config,
    })
