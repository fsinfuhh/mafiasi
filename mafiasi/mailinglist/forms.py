from __future__ import unicode_literals

from django import forms
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _

class AddWhitelistForm(forms.Form):
    email = forms.EmailField()
    
    def __init__(self, *args, **kwargs):
        self.mailinglist = kwargs.pop('mailinglist')
        super(AddWhitelistForm, self).__init__(*args, **kwargs)

    def validate_email(self):
        email = self.cleaned_data['email'].lower()
        if self.mailinglist.whitelist_addresses.filter(email=email).count():
            raise forms.ValidationError(
                    _('This email is already on the whitelist'))
        return self.cleaned_data

    def save(self):
        email = self.cleaned_data['email'].lower()
        try:
            self.mailinglist.whitelist_addresses.create(email=email)
        except IntegrityError:
            pass
