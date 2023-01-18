from django import forms
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _

from mafiasi.mailinglist.models import Mailinglist


class AddWhitelistForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.mailinglist = kwargs.pop("mailinglist")
        super(AddWhitelistForm, self).__init__(*args, **kwargs)

    def validate_email(self):
        email = self.cleaned_data["email"].lower()
        if self.mailinglist.whitelist_addresses.filter(email=email).count():
            raise forms.ValidationError(_("This email is already on the whitelist"))
        return self.cleaned_data

    def save(self):
        email = self.cleaned_data["email"].lower()
        try:
            self.mailinglist.whitelist_addresses.create(email=email)
        except IntegrityError:
            pass


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Mailinglist
        fields = ("allow_others",)
