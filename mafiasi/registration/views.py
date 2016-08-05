from smtplib import SMTPRecipientsRefused

from nameparser import HumanName

from django.core import signing
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from mafiasi.base.models import Yeargroup, Mafiasi, PasswdEntry
from mafiasi.registration.models import create_mafiasi_account
from mafiasi.registration.forms import (RegisterForm, AdditionalInfoForm,
                                        PasswordForm, NickChangeForm,
                                        EmailChangeForm)

TOKEN_MAX_AGE = 3600 * 24

def request_account(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['account']
            domain = form.cleaned_data['domain']
            if domain == settings.PRIMARY_DOMAIN:
                yeargroup = Yeargroup.objects.get_by_account(account)
                if yeargroup:                     
                    return _finish_account_request(request, {
                        'action': 'request_account',
                        'account': account,
                        'domain': domain,
                        'yeargroup_pk': yeargroup.pk
                    })
                else:
                    info_form = AdditionalInfoForm()
                    info_form.prefill(account, domain)
                    return TemplateResponse(request,
                        'registration/require_info.html', {
                            'account': account,
                            'info_form': info_form,
                    })
            else:
                info_form = AdditionalInfoForm()
                info_form.prefill(account, domain)
                return TemplateResponse(request,
                    'registration/require_info_other.html', {
                        'account': account,
                        'domain': domain,
                        'info_form': info_form,
                    })

    else:
        form = RegisterForm()

    return TemplateResponse(request, 'registration/request_account.html', {
            'form': form,
        })


@require_POST
def additional_info(request):
    if request.POST:
        form = AdditionalInfoForm(request.POST)
        if form.is_valid():
            return _finish_account_request(request, {
                        'action': 'request_account',
                        'account': form.cleaned_data['account'],
                        'domain': form.cleaned_data['domain'],
                        'first_name': form.cleaned_data['first_name'],
                        'last_name': form.cleaned_data['last_name'],
                        'yeargroup_pk': form.cleaned_data['yeargroup'].pk
                    })

    if not 'domain' in form.cleaned_data or not 'account' in form.cleaned_data:
        return redirect('registration_request_account')
    else:
        domain = form.cleaned_data['domain']
        account = form.cleaned_data['account']

    if domain == settings.PRIMARY_DOMAIN:
        template = 'registration/require_info.html'
    else:
        template = 'registration/require_info_other.html'
    form.prefill(account, domain)

    return TemplateResponse(request, template, {
        'account': account,
        'domain': domain,
        'info_form': form,
    })


def request_successful(request, email):
    return TemplateResponse(request, 'registration/request_successful.html', {
        'email': email
    })

def _create_username(info, yeargroup):
    if info['account'][0].isdigit():
        return yeargroup.slug[2] + info['account']
    elif info['domain'] != settings.PRIMARY_DOMAIN:
        return "{}.{}".format(
            info['account'],
            settings.REGISTER_DOMAIN_MAPPING[info['domain']])
    else:
        return info['account']

def create_account(request, info_token):
    if request.user.is_authenticated():
        return redirect('dashboard_index')

    try:
        info = signing.loads(info_token, max_age=TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        return TemplateResponse(request, 'registration/token_expired.html')
    except signing.BadSignature:
        return TemplateResponse(request, 'registration/token_invalid.html')

    yeargroup = Yeargroup.objects.get(pk=info['yeargroup_pk'])
    username = _create_username(info, yeargroup)

    if Mafiasi.objects.filter(username=username).exists():
        return redirect('login')

    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            first_name = info.get('first_name')
            last_name = info.get('last_name')
            if not (first_name and last_name):
                if info['domain'] == settings.PRIMARY_DOMAIN:
                    try:
                        passwd = PasswdEntry.objects.get(username=info['account'])
                        name_parsed = HumanName(passwd.full_name)
                        first_name = name_parsed.first
                        last_name = name_parsed.last
                    except PasswdEntry.DoesNotExist:
                        # This happens only when someone removed an entry
                        # from our passwd database manually
                        pass
                else:
                    return TemplateResponse(request,
                                            'registration/token_invalid.html')
            email = u'{0}@{1}'.format(info['account'], info['domain'])
            mafiasi = create_mafiasi_account(username=username,
                                             email=email,
                                             first_name=first_name,
                                             last_name=last_name,
                                             account=info['account'],
                                             yeargroup=yeargroup,
                                             is_student=True)
            mafiasi.set_password(form.cleaned_data['password1'])
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

@login_required
def account_settings(request):
    password_change_form = PasswordChangeForm(request.user)
    nick_change_form = NickChangeForm(request.user)
    email_change_form = EmailChangeForm(request.user)

    form = request.POST.get('form')
    if form == 'change_pw':
        password_change_form = PasswordChangeForm(request.user, request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            messages.success(request, _("Password was changed."))
            return redirect('registration_account')
    elif form == 'change_nick':
        nick_change_form = NickChangeForm(request.user, request.POST)
        if nick_change_form.is_valid():
            nick_change_form.save()
            messages.success(request, _('Your nickname is now {}.').format(
                nick_change_form.cleaned_data['nickname']))
            return redirect('registration_account')
    elif form == 'change_email':
        email_change_form = EmailChangeForm(request.user, request.POST)
        if email_change_form.is_valid():
            return _verify_email(request,
                                 email_change_form.cleaned_data['email'])
    
    return TemplateResponse(request, 'registration/account.html', {
        'password_change_form': password_change_form,
        'nick_change_form': nick_change_form,
        'email_change_form': email_change_form,
        'username': request.user.username,
    })

@login_required
def change_email(request, token):
    try:
        data = signing.loads(token, max_age=TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        return TemplateResponse(request, 'registration/token_expired.html')
    except signing.BadSignature:
        return TemplateResponse(request, 'registration/token_invalid.html')
    if request.user.username != data.get('username'):
        return TemplateResponse(request, 'registration/token_invalid.html')
    email = data.get('email')
    try:
        validate_email(email)
    except ValidationError:
        return TemplateResponse(request, 'registration/token_invalid.html')
    if settings.MAILCLOAK_DOMAIN:
        request.user.email = email
    request.user.real_email = email
    request.user.save()

    messages.success(request, _('Your email address has been changed.'))
    return redirect('registration_account')

def _verify_email(request, email):
    token = signing.dumps({
        'email': email,
        'username': request.user.username,
    })
    url_path = reverse('registration_change_email', args=(token,))
    link = request.build_absolute_uri(url_path)
    email_content = render_to_string('registration/email_verify.txt', {
        'username': request.user.username,
        'email': email,
        'link': link,
    })
    return _send_mail_or_error_page(_('Verify this address for %s' % settings.PROJECT_NAME),
                                    email_content, email, request)

def _finish_account_request(request, info):
    email = u'{0}@{1}'.format(info['account'], info['domain'])
    token = signing.dumps(info)
    url_path = reverse('registration_create_account', args=(token,))
    activation_link = request.build_absolute_uri(url_path)
    email_content = render_to_string('registration/create_email.html', {
        'activation_link': activation_link
    })
    return _send_mail_or_error_page(_('Account creation at %s' % settings.PROJECT_NAME),
                                    email_content, email, request)
    
def _send_mail_or_error_page(subject, content, address, request):
    try:
        send_mail(subject, content, None, [address])
        if settings.DEBUG:
            print(u"VALIDATION MAIL to {0}\nSubject: {1}\n{2}".format(
                address, subject, content))
    except SMTPRecipientsRefused as e:
        wrong_email, (error_code, error_msg) = e.recipients.items()[0]
        unknown = 'User unknown' in error_msg
        if not unknown:
            error_email_content = u'{0}: {1}'.format(e.__class__.__name__,
                                                     repr(e.recipients))
            send_mail(
                    _('Registration: Sending mail failed: {}'.format(address)),
                    error_email_content,
                    None,
                    [settings.TEAM_EMAIL])
        return TemplateResponse(request, 'registration/email_error.html', {
            'unkown': unknown,
            'error_code': error_code,
            'error_msg': error_msg,
            'recipient': wrong_email
        })

    return redirect('registration_request_successful', address)
