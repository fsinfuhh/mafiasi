import re

from django import forms
from django.utils.translation import gettext_lazy as _

from mafiasi import settings
from mafiasi.base.models import Mafiasi, Yeargroup


class RegisterForm(forms.Form):
    account = forms.CharField()
    domain = forms.ChoiceField(
        choices=[(v, v) for v in settings.REGISTER_DOMAINS])

    def clean_account(self):
        domain = self.data['domain']
        account = self.cleaned_data['account'].lower()

        if domain not in settings.ACCOUNT_PATTERNS:
            # no pattern given, accept everything
            return account

        if not re.fullmatch(settings.ACCOUNT_PATTERNS[domain], account):
            raise forms.ValidationError(_('That does not look like a valid account name for {}.').format(domain))

        return account


class AdditionalInfoForm(forms.Form):
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)
    account = forms.CharField(max_length=64)
    domain = forms.ChoiceField(choices=[(v, v) for v in settings.REGISTER_DOMAINS])
    yeargroup = forms.ModelChoiceField(queryset=Yeargroup.objects.all(),
                                       required=False)

    def _yeargroups_for_account(self, account):
        if account[0].isdigit():
            group_name = '___{0}'.format(account[0])
            where = ["slug LIKE '{0}'".format(group_name)]
            return Yeargroup.objects.extra(where=where)
        else:
            return Yeargroup.objects.order_by('name')

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
            yeargroup = Yeargroup.objects.get_by_domain(domain)
            # Get queryset
            yeargroups = Yeargroup.objects.filter(id=yeargroup.id).order_by('name')

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
