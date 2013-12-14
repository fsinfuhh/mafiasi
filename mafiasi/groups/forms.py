from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from mafiasi.groups.models import GroupInvitation

class InvitationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')
        self.user = kwargs.pop('user')
        super(InvitationForm, self).__init__(*args, **kwargs)

    invitee = forms.CharField()
    invitee_user = None

    def clean_invitee(self):
        invitee = self.cleaned_data['invitee']
        User = get_user_model()
        try:
            invitee_user = User.objects.get(username=invitee)
            self.invitee_user = invitee_user
        except User.DoesNotExist:
            raise forms.ValidationError(_('No such user.'))

        has_invitation = bool(GroupInvitation.objects.filter(
                group=self.group, invitee=invitee_user))

        if has_invitation:
            raise forms.ValidationError(_('User already has an invitation.'))
        
        return invitee

    def get_invitation(self):
        return GroupInvitation(group=self.group,
                               invitee=self.invitee_user,
                               invited_by=self.user)

    def save(self):
        self.get_invitation().save()
