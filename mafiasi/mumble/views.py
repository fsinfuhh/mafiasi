from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from mafiasi.registration.forms import CheckPasswordForm
from mafiasi.mumble.models import get_account, create_account

def index(request):
    return TemplateResponse(request, 'mumble/index.html', {
        'mumble_domain': settings.MUMBLE_DOMAIN,
        'cert_fingerprint': settings.MUMBLE_CERT_FINGERPRINT
    })

@login_required
def create(request):
    if get_account(request.user) is not None:
        return redirect('mumble_password_reset')
    
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

    return TemplateResponse(request, 'mumble/create.html', {
        'form': form
    })

@login_required
def password_reset(request):
    account = get_account(request.user)
    if account is None:
        return redirect('mumble_create')

    if request.method == 'POST':
        form = CheckPasswordForm(request.POST, user=request.user)
        if form.is_valid():
            password = form.cleaned_data['password']
            # SET PASSWORD
            messages.success(request, _("Password was changed."))
            return redirect('mumble_index')
    else:
        form = CheckPasswordForm(user=request.user)

    return TemplateResponse(request, 'mumble/password_reset.html', {
        'form': form
    })
