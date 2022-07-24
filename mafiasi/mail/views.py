

from django.conf import settings
from django.template.response import HttpResponse

from mafiasi.base.decorators import require_auth
from mafiasi.mail.signals import (CollectMail, collect_mailaddresses,
                                  mailaddresses_known)

@require_auth(username='mail', password=settings.EMAIL_ADDRESSES_PASSWORD)
def mailaddresses(request):
    """Return a list of all valid mailaddresses."""
    addresses = []
    collect_mailaddresses.send_robust(sender=CollectMail, addresses=addresses)
    addresses += settings.VALID_EMAIL_ADDRESSES
    output = '\n'.join(address for address in addresses) + '\n'
    mailaddresses_known.send_robust(sender=CollectMail)
    return HttpResponse(output.encode('utf-8'), content_type='text/plain')

