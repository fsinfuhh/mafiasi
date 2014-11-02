from __future__ import unicode_literals

from django.conf import settings
from django.template.response import HttpResponse
from django.contrib.auth.models import Group

from mafiasi.base.decorators import require_auth

@require_auth(username='mail', password=settings.EMAIL_ADDRESSES_PASSWORD)
def mailaddresses(request):
    """Return a list of all valid mailaddresses."""
    addresses = []
    groups = Group.objects.filter(properties__has_mailinglist=True)
    for group in groups:
        addresses.append('{}@{}'.format(group.name, settings.LIST_DOMAIN))
    addresses += settings.VALID_EMAIL_ADDRESSES
    output = '\n'.join(address + ' OK' for address in addresses) + '\n'
    return HttpResponse(output.encode('utf-8'), content_type='text/plain')

