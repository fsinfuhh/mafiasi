# coding=utf-8


from smtplib import SMTPRecipientsRefused

import requests
from authFun import create_invitation, delete_invitation, invitation_exists
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from mafiasi.base.models import Mafiasi
from mafiasi.groups.models import GroupProxy
from mafiasi.guests.forms import InvitationForm
from mafiasi.guests.models import Guest, Invitation, get_invitation_bucket
from mafiasi.registration.forms import PasswordForm

from .authFun import AuthentikUserError


@login_required
def index(request):
    if request.user.is_guest:
        return redirect("guests_invited_by")

    invitations = Invitation.objects.select_related().filter(invited_by=request.user).order_by("-date_invited")
    guests = Guest.objects.select_related().filter(invited_by=request.user).order_by("guest_user__username")
    return render(
        request,
        "guests/index.html",
        {"invitations": invitations, "guests": guests, "guest_extension": settings.GUEST_EXTENSION},
    )


@login_required
def invite(request):
    if request.user.is_guest:
        return redirect("guest_invited_by")

    if request.method == "POST":
        form = InvitationForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    invitation = form.save(commit=False)
                    invitation.invited_by = request.user
                    invitation.save()
                    create_invitation(
                        username=invitation.username,
                        first_name=invitation.first_name,
                        last_name=invitation.last_name,
                        email=invitation.email,
                    )
            except (AuthentikUserError, requests.RequestException):
                form.add_error(None, _("Could not create the account right now, please try again."))
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
    invitation = get_object_or_404(Invitation, pk=invitation_pk)
    if request.method == "POST":
        if invitation.invited_by != request.user:
            raise PermissionDenied()
        if "withdraw" in request.POST:
            delete_invitation(invitation.username)
            invitation.delete()
            messages.success(request, _("Invitation was withdrawn."))
        elif "resend" in request.POST:
            try:
                if not invitation_exists(str(invitation.authentik_pk)):
                    messages.error(request, _("This invitation was already used or expired."))
                    return redirect("guests_index")
            except requests.RequestException:
                messages.error(request, _("Could not resend right now, please try again."))
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
