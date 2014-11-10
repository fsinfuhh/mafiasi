import re

from django import forms
from django.utils.translation import ugettext as _

from mafiasi.guests.models import Invitation, get_invitation_bucket

_username_re = re.compile(r'^[a-z][a-z0-9]+$')
class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(InvitationForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if _username_re.match(username) is None:
            raise forms.ValidationError(
                _('Username must be alphanumeric and start with a letter.'))
        if len(username) < 3:
            raise forms.ValidationError(
                _('Username must be at least 3 characters long.'))
        return username

    def clean(self):
        cleaned_data = super(InvitationForm, self).clean()
        bucket = get_invitation_bucket(self.user, _('invitations'))
        try:
            bucket.consume(1)
        except bucket.TokensExceeded as e:
            raise forms.ValidationError(e.get_message())
        return cleaned_data
