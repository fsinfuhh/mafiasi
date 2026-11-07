import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from mafiasi.guests.forms import InvitationForm
from mafiasi.guests.models import Invitation, get_invitation_bucket

from .auth_fun import create_invitation, delete_invitation, getOpenInvitations, invitation_exists


@login_required
def index(request):
    if request.user.is_guest:
        raise PermissionDenied()
    invitations = getOpenInvitations(request.user.username)
    guests = []
    return render(
        request,
        "guests/index.html",
        {"invitations": invitations, "guests": guests, "guest_extension": settings.GUEST_EXTENSION},
    )


@login_required
def invite(request):
    if request.user.is_guest:
        raise PermissionDenied()
    if request.method == "POST":
        form = InvitationForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    invitation = form.save(commit=False)
                    invitation.invited_by = request.user.username
                    invitation.save()
                    inv = create_invitation(
                        inviter_uid=request.user.username,
                        username=invitation.username + settings.GUEST_EXTENSION,
                        first_name=invitation.first_name,
                        last_name=invitation.last_name,
                        email=invitation.email,
                    )
                invitation.authentik_pk = inv["pk"]
                invitation.save()
            except requests.RequestException:
                form.add_error(None, _("Could not create the account right now, please try again later."))
            else:
                invitation.send_email(request)
                msg = _("{} was successfully invited.").format(invitation.username)
                messages.success(request, msg)
                return redirect("guests_index")
    else:
        form = InvitationForm(user=request.user)
    return render(
        request,
        "guests/invite.html",
        {
            "form": form,
            "guest_extension": settings.GUEST_EXTENSION,
        },
    )


@login_required
def invitation_action(request):
    invitation_pk = request.POST.get("invitation_pk")
    invitation = get_object_or_404(Invitation, pk=invitation_pk, invited_by=request.user.username)
    if request.method == "POST":
        if "withdraw" in request.POST:
            if invitation.authentik_pk:
                try:
                    delete_invitation(str(invitation.authentik_pk), request.user.username)
                except requests.RequestException:
                    messages.error(request, _("Could not withdraw the invitation right now, please try again later."))
                    return redirect("guests_index")
            invitation.delete()
            messages.success(request, _("Invitation was withdrawn."))
        elif "resend" in request.POST:
            try:
                if not invitation_exists(str(invitation.authentik_pk)):
                    messages.error(request, _("This invitation was already used or expired."))
                    return redirect("guests_index")
            except requests.RequestException:
                messages.error(request, _("Could not resend right now, please try again later."))
                return redirect("guests_index")
            bucket = get_invitation_bucket(request.user, _("invitation mails"))
            try:
                bucket.consume(1)
            except bucket.TokensExceeded as e:
                messages.error(request, e.get_message())
            else:
                invitation.send_email(request)
                messages.success(request, _("Invitation mail was resent."))
    return redirect("guests_index")
