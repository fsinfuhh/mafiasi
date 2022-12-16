from io import BytesIO

import gpgme

from django import forms
from django.utils.translation import gettext_lazy as _

class ImportForm(forms.Form):
    keys = forms.CharField(widget=forms.Textarea())
    imported_keys = []

    def clean_keys(self):
        ctx = gpgme.Context()
        encoded_keys = self.cleaned_data['keys'].encode('utf-8')
        result = ctx.import_(BytesIO(encoded_keys))
        if result.considered == 0:
            raise forms.ValidationError(_("No valid OpenPGP keys."))
        self.imported_keys = [key[0] for key in result.imports]
        return self.cleaned_data
