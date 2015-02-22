import re

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

        # Workaround for bug in pydiscourse.sso: It creates a nonce which
        # looks like "6ec2d11456ecba485823f791a468a4cd&return_sso_url",
        # so just remove the &return_sso_url
        if '&' in nonce:
            nonce = nonce.split('&')[0]

        # FIXME Add nickname to ldap as seperate field
        nickname = re.sub(r'(.+)\s\((.+)\)$', r'\1',
                          request.user.get_ldapuser().display_name)
        url = sso_redirect_url(nonce,
                               settings.DISCOURSE_SSO_SECRET,
                               request.user.email,
                               request.user.username,
                               request.user.username,
                               name=nickname)

    except DiscourseError:
        return HttpResponse(status=400)
    return redirect(settings.DISCOURSE_URL + url)
