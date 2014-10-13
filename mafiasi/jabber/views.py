from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from mafiasi.registration.forms import CheckPasswordForm
from mafiasi.jabber.models import get_account, create_account

def index(request):
    jabber_user = get_account(request.user)
    if request.user.is_authenticated():
        user_display_name = request.user.get_ldapuser().display_name
    else:
        user_display_name = ""

    return TemplateResponse(request, 'jabber/index.html', {
        'jabber_user': jabber_user,
        'user_display_name': user_display_name,
        'jabber_domain': settings.JABBER_DOMAIN,
        'cert_fingerprint': settings.JABBER_CERT_FINGERPRINT
    })

@login_required
def create(request):
    if get_account(request.user) is not None:
        return redirect('jabber_index')
    
    if request.method == 'POST':
        form = CheckPasswordForm(request.POST, user=request.user)
        if form.is_valid():
            password = form.cleaned_data['password']
            status, user = create_account(request.user, password)
            if status == 'created':
                messages.success(request, _('Account was created.'))
            elif status == 'exists':
                messages.warning(request, _('Account already exists.'))
            else:
                messages.error(request, _('Sorry, we had an internal error.'))
            return redirect('jabber_index')
    else:
        form = CheckPasswordForm(user=request.user)

    return TemplateResponse(request, 'jabber/create.html', {
        'form': form
    })
