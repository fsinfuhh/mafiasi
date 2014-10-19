from django import template
from mafiasi.groups.models import GroupInvitation

register = template.Library()
@register.assignment_tag(takes_context=True)
def open_invitations(context):
    user = context['user']
    if user.is_authenticated():
        return GroupInvitation.objects.filter(
                invitee=user
            ).count()
