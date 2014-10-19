import re

from django import forms
from django.utils.translation import gettext_lazy as _

from mafiasi import settings
from mafiasi.base.models import Yeargroup

class RegisterForm(forms.Form):
    account = forms.CharField()
    domain = forms.ChoiceField(
        choices=[(v,v) for v in settings.REGISTER_DOMAINS])

    def clean_account(self):
        account = self.cleaned_data['account'].lower()
        if u'@' in account:
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
            group_name = u'___{0}'.format(account[0])
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
        ldap_user.display_name = u"{} ({})".format(
                self.cleaned_data['nickname'], self.user.username)
        ldap_user.save()

class EmailChangeForm(forms.Form):
    email = forms.EmailField()