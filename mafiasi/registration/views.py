from smtplib import SMTPRecipientsRefused

from nameparser import HumanName

from django.core import signing
from django.urls import reverse
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

from mafiasi.base.models import Yeargroup, Mafiasi
from mafiasi.registration.utils import get_irz_ldap_entry, get_irz_ldap_group
from mafiasi.registration.models import create_mafiasi_account
from mafiasi.registration.forms import (AdditionalInfoForm, PasswordForm, NickChangeForm,
                                        EmailChangeForm, PrimaryRegisterForm, OtherRegisterForm)

TOKEN_MAX_AGE = 3600 * 24


def request_account(request):
    if request.method == 'POST':
        is_primary = request.POST['domain'] == settings.PRIMARY_DOMAIN
        if is_primary:
            form = PrimaryRegisterForm(request.POST)
        else:
            form = OtherRegisterForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['account']
            domain = form.cleaned_data['domain']
            if domain == settings.PRIMARY_DOMAIN:
                user = get_irz_ldap_entry(uid=account)
                if user is None:
                    # Nobody is supposed to know that this account does not exist. Therefore, pretend success.
                    return TemplateResponse(request, 'registration/request_successful.html', {'email': None})
                irz_group_slug = get_irz_ldap_group(user['gid'])
                if irz_group_slug is None:
                    # this should not happen because all groups used in the LDAP should also exist there
                    raise AssertionError(f'The yeargroup {user["gid"]} was referenced in the IRZ LDAP '
                                         'but does not actually exist there.')

                # Our group slugs do not contain the leading 'j'
                group_slug = irz_group_slug.lstrip('j')

                try:
                    # Try to find the group with the same slug.
                    yeargroup = Yeargroup.objects.get(slug=group_slug)
                except Yeargroup.DoesNotExist:
                    if account[0].isdigit():
                        # This should usually only happen once a year, when the first user
                        # of the new yeargroup fills out the registration form.
                        yeargroup = Yeargroup(slug=group_slug, name=group_slug, gid=user['gid'])
                        yeargroup.save()
                    else:
                        # All accounts that start with another letter than a digit are employee
                        # accounts and should be treated as such. Further differentiation by their
                        # actual groups (which correspond to the research groups) is not necessary.
                        yeargroup = Yeargroup.objects.get_or_create(slug='employee', defaults={'name': 'Employee'})

                return _finish_account_request(request, {
                    'action': 'request_account',
                    'account': account,
                    'domain': domain,
                    'yeargroup_pk': yeargroup.pk,
                    'email': user['email'],
                })
            else:
                # here we need all the information because these users are not in the registration LDAP
                info_form = AdditionalInfoForm()
                info_form.prefill(account, domain)
                return TemplateResponse(request,
                    'registration/require_info_other.html', {
                        'account': account,
                        'domain': domain,
                        'info_form': info_form,
                    })
        else:
            return TemplateResponse(request, 'registration/request_account.html', {
                'form_principal': form if is_primary else PrimaryRegisterForm(),
                'form_other': OtherRegisterForm() if is_primary else form,
                'is_primary': is_primary,
            })

    form = PrimaryRegisterForm(initial={'domain': settings.PRIMARY_DOMAIN})

    return TemplateResponse(request, 'registration/request_account.html', {
            'form_principal': form,
            'form_other': OtherRegisterForm(),
            'is_primary': True,
        })


@require_POST
def additional_info(request):
    form = AdditionalInfoForm(request.POST)
    if form.is_valid():
        account = form.cleaned_data['account']
        domain = form.cleaned_data['domain']
        return _finish_account_request(request, {
                    'action': 'request_account',
                    'domain': domain,
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'yeargroup_pk': form.cleaned_data['yeargroup'].pk,
                    'email': f'{account}@{domain}',
                    'account': account,
                })


def request_successful(request):
    return TemplateResponse(request, 'registration/request_successful.html')


def _create_username(info, yeargroup):
    if info['domain'] != settings.PRIMARY_DOMAIN:
        return "{}.{}".format(
            info['account'],
            settings.REGISTER_DOMAIN_MAPPING[info['domain']])
    elif info['account'][0].isdigit():
        return yeargroup.slug[2] + info['account']
    else:
        return info['account']


def create_account(request, info_token):
    if request.user.is_authenticated:
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
            if info['domain'] == settings.PRIMARY_DOMAIN:
                # Get information from IRZ LDAP
                user = get_irz_ldap_entry(uid=info['account'])
                email = user['email']
                name_parsed = HumanName(user['name'])
                first_name = name_parsed.first
                last_name = name_parsed.last
            else:
                first_name = info.get('first_name')
                last_name = info.get('last_name')
                email = '{0}@{1}'.format(info['account'], info['domain'])

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
    if not settings.MAILCLOAK_DOMAIN:
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
                                    email_content, email, request, email)


def _finish_account_request(request, info):
    email = info.pop('email')
    token = signing.dumps(info)
    url_path = reverse('registration_create_account', args=(token,))
    activation_link = request.build_absolute_uri(url_path)
    email_content = render_to_string('registration/create_email.html', {
        'activation_link': activation_link,
    })
    # Registration was with email for all domains except the primary domain
    if info['domain'] == settings.PRIMARY_DOMAIN:
        # For the primary domain, don't leak the person's mail address
        email_shown = None
    else:
        email_shown = email
    return _send_mail_or_error_page(_('Account creation at %s' % settings.PROJECT_NAME),
                                    email_content, email, request, email_shown)


def _send_mail_or_error_page(subject, content, address, request, email_shown):
    try:
        send_mail(subject, content, None, [address])
        if settings.DEBUG:
            print(("VALIDATION MAIL to {0}\nSubject: {1}\n{2}".format(
                address, subject, content)))
    except SMTPRecipientsRefused as e:
        wrong_email, (error_code, error_msg) = list(e.recipients.items())[0]
        unknown = 'User unknown' in error_msg.decode()
        if not unknown:
            error_email_content = '{0}: {1}'.format(e.__class__.__name__,
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

    return TemplateResponse(request, 'registration/request_successful.html', {
        'email': email_shown,
    })
