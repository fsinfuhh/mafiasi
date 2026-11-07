import re

from django import forms
from django.conf import settings
from django.contrib.sites import requests
from django.utils.translation import gettext as _

from mafiasi.guests.models import Invitation, get_invitation_bucket

from .authFun import mail_exists, uid_exists

_username_re = re.compile(r"^[a-z][a-z0-9.\-]+$")


class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if _username_re.fullmatch(username) is None:
            raise forms.ValidationError(_("Username must be alphanumeric and start with a letter."))

        if len(username) < 3:
            raise forms.ValidationError(_("Username must be at least 3 characters long."))

        full_uid = username + settings.GUEST_EXTENSION

        try:
            if uid_exists(full_uid):
                raise forms.ValidationError(_("This name is not available."))
        except requests.RequestException:
            raise forms.ValidationError(_("Can't verify the username right now, please try again later."))

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        domain = email.rsplit("@", 1)[1]
        if domain in settings.REGISTER_DOMAINS:
            raise forms.ValidationError(_("The guest can use this email address to register a normal user account."))

        try:
            if mail_exists(email):
                raise forms.ValidationError(_("There is already an account with that email."))
        except requests.RequestException:
            raise forms.ValidationError(_("Can't verify the email right now, please try again later."))

        return email

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data
        bucket = get_invitation_bucket(self.user, _("invitations"))
        try:
            bucket.consume(1)
        except bucket.TokensExceeded as e:
            raise forms.ValidationError(e.get_message())
        return cleaned_data
