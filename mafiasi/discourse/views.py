from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from pydiscourse.sso import sso_validate, sso_redirect_url, DiscourseError

from mafiasi import settings

@login_required
def sso(request):
    try:
        payload = request.GET.get('sso')
        sig = request.GET.get('sig')
        nonce = sso_validate(payload, sig, settings.DISCOURSE_SSO_SECRET)
        dn = request.user.get_ldapuser().display_name
        url = sso_redirect_url(nonce,
                               settings.DISCOURSE_SSO_SECRET,
                               request.user.email,
                               request.user.username,
                               request.user.username,
                               name=dn)

    except DiscourseError:
        return HttpResponse(status=400)
    return redirect(settings.DISCOURSE_URL + url)
