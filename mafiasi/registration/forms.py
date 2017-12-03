import re

from django import forms
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site

from mafiasi import settings
from mafiasi.base.models import Mafiasi, Yeargroup

class RegisterForm(forms.Form):
    account = forms.CharField()
    domain = forms.ChoiceField(
        choices=[(v,v) for v in settings.REGISTER_DOMAINS])

    def clean_account(self):
        account = self.cleaned_data['account'].lower()
        if '@' in account:
            account, _domain = account.split('@', 1)
        if not account.isalnum():
            raise forms.ValidationError(_('Invalid account name'))
        return account

class AdditionalInfoForm(forms.Form):
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)
    account = forms.CharField(max_length=16)
    domain = forms.ChoiceField(
        choices=[(v,v) for v in settings.REGISTER_DOMAINS])
    yeargroup = forms.ModelChoiceField(queryset=Yeargroup.objects.all(),
                                       required=False)

    def _yeargroups_for_account(self, account):
        if account[0].isdigit():
            group_name = '___{0}'.format(account[0])
            where = ["slug LIKE '{0}'".format(group_name)]
            return Yeargroup.objects.extra(where=where)
        else:
            return Yeargroup.objects.all()

    def clean(self):
        account = self.cleaned_data['account']
        domain = self.cleaned_data['domain']
        if domain != settings.PRIMARY_DOMAIN:
            try:
                self.cleaned_data['yeargroup'] = \
                    Yeargroup.objects.get_by_domain(domain)
            except KeyError:
                raise forms.ValidationError(_('Invalid domain'))
        else:
            if not 'yeargroup' in self.cleaned_data:
                raise forms.ValidationError(_('This field is required.'))
            if not self.cleaned_data['yeargroup'] in \
                self._yeargroups_for_account(account):
                raise forms.ValidationError(_('Invalid yeargroup selected'))
        return self.cleaned_data

    def prefill(self, account, domain):
        if domain == settings.PRIMARY_DOMAIN:
            yeargroups = self._yeargroups_for_account(account)
        else:
            yeargroups = [Yeargroup.objects.get_by_domain(domain)]

        self.fields["yeargroup"].queryset = yeargroups

class PasswordForm(forms.Form):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput
    )   
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput
    )   

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    _("The two password fields didn't match."))
        return password2


class CheckPasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CheckPasswordForm, self).__init__(*args, **kwargs)

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput
    )   
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if not self.user.check_password(password):
                raise forms.ValidationError(_("Wrong password."))
        return password

class NickChangeForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        ldap_user = user.get_ldapuser()
        nickname = re.sub(r'(.+)\s\((.+)\)$', r'\1', ldap_user.display_name)
        kwargs['initial'] = {
            'nickname': nickname
        }
        super(NickChangeForm, self).__init__(*args, **kwargs)
    
    nickname = forms.CharField(max_length=20)
    
    def save(self):
        ldap_user = self.user.get_ldapuser()
        ldap_user.display_name = "{} ({})".format(
                self.cleaned_data['nickname'], self.user.username)
        ldap_user.save()


class EmailChangeForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, user, *args, **kwargs):
        kwargs['initial'] = {
            'email': user.real_email,
        }
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if Mafiasi.objects.filter(real_email=email).count() > 0:
            raise forms.ValidationError(
                _('This address is already associated with an account.'))

        if email.endswith(settings.MAILINGLIST_DOMAIN):
            raise forms.ValidationError(
                _('Group addresses cannot be used for this purpose.'))
        elif email.endswith(settings.MAILCLOAK_DOMAIN):
            raise forms.ValidationError(
                _('Cloak adresses cannot be used for this purpose.'))

        return email


class PasswordResetForm(forms.Form):
    """
    This is just copied from django/contrib/auth/forms.py with email
    changed to real_email.
    """
    email = forms.EmailField(label=_("Email"), max_length=254)

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        active_users = UserModel._default_manager.filter(
            real_email__iexact=email, is_active=True)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context is not None:
                c.update(extra_email_context)

            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)

            if html_email_template_name:
                html_email = loader.render_to_string(html_email_template_name, c)
            else:
                html_email = None
            send_mail(subject, email, from_email, [user.email], html_message=html_email)
