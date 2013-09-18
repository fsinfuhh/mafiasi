from django.core import signing
from django.template.response import TemplateResponse
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login

from mafiasi.base.models import Yeargroup, Mafiasi
from mafiasi.registration.forms import RegisterForm, AdditionalInfoForm, PasswordForm

TOKEN_MAX_AGE = 3600 * 24

def request_account(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['account']
            yeargroup = Yeargroup.objects.get_by_account(account)
            if not yeargroup:
                info_form = AdditionalInfoForm(request.POST, account=account)
                if info_form.is_valid():
                    return _finish_account_request({
                        'action': 'request_account',
                        'account': account,
                        'first_name': info_form.cleaned_data['first_name'],
                        'last_name': info_form.cleaned_data['last_name'],
                        'yeargroup_pk': info_form.cleaned_data['yeargroup'].pk
                    })
                return TemplateResponse(request, 'registration/require_info.html', {
                    'account': account,
                    'info_form': info_form
                })
            else:
                return _finish_account_request({
                    'action': 'request_account',
                    'account': account,
                    'yeargroup_pk': yeargroup.pk
                })
    else:
        form = RegisterForm()

    return TemplateResponse(request, 'registration/request_account.html', {
        'form': form,
        'email_domain': settings.EMAIL_DOMAIN
    })

def request_successful(request, account):
    email = u'{0}@{1}'.format(account, settings.EMAIL_DOMAIN)
    return TemplateResponse(request, 'registration/request_successful.html', {
        'email': email
    })

def create_account(request, info_token):
    if request.user:
        return redirect('dashboard_index')

    try:
        info = signing.loads(info_token, max_age=TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        return TemplateResponse(request, 'registration/token_expired.html')
    except signing.BadSignature:
        return TemplateResponse(request, 'registration/token_invalid.html')

    yeargroup = Yeargroup.objects.get(pk=info['yeargroup_pk'])
    if info['account'][0].isdigit():
        username = yeargroup.slug[2] + info['account']
    else:
        username = info['account']

    if Mafiasi.objects.filter(username=username).count():
        return redirect('login')

    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            mafiasi = Mafiasi(username=username)
            mafiasi.set_password(form.cleaned_data['password1'])
            first_name = info.get('first_name')
            last_name = info.get('last_name')
            yeargroup = Yeargroup.objects.get(pk=info['yeargroup_pk'])
            if first_name and last_name:
                mafiasi.first_name = first_name
                mafiasi.last_name = last_name
            mafiasi.yeargroup = yeargroup
            mafiasi.save()
            mafiasi.backend='django.contrib.auth.backends.ModelBackend'
            login(request, mafiasi)
            return redirect('dashboard_index')
    else:
        form = PasswordForm()

    return TemplateResponse(request, 'registration/create_account.html', {
        'form': form,
        'username': username
    })

            

def _finish_account_request(info):
    email = u'{0}@{1}'.format(info['account'], settings.EMAIL_DOMAIN)
    token = signing.dumps(info)
    url = None
    # TODO: Send email
    return redirect('registration_request_successful', info['account'])
