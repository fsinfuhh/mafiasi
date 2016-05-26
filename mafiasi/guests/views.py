from __future__ import unicode_literals

from django.core import signing
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from mafiasi.base.models import Mafiasi
from mafiasi.registration.forms import PasswordForm
from mafiasi.guests.models import Invitation, Guest, get_invitation_bucket
from mafiasi.guests.forms import InvitationForm

@login_required
def index(request):
    if request.user.is_guest:
        return redirect('guests_invited_by')

    invitations = (Invitation.objects.select_related()
                   .filter(invited_by=request.user)
                   .order_by('-date_invited'))
    guests = (Guest.objects.select_related()
              .filter(invited_by=request.user)
              .order_by('guest_user__username'))
    return render(request, 'guests/index.html', {
        'invitations': invitations,
        'guests': guests
    })

@login_required
def invite(request):
    if request.user.is_guest:
        return redirect('guest_invited_by')

    if request.method == 'POST':
        form = InvitationForm(request.POST, user=request.user)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.invited_by = request.user
            invitation.save()
            invitation.send_email()
            msg = _('{} was successfully invited.').format(invitation.username)
            messages.success(request, msg)
            return redirect('guests_index')
    else:
        form = InvitationForm(user=request.user)
    return render(request, 'guests/invite.html', {
        'form': form,
        'guest_extension': settings.GUEST_EXTENSION,
    })

@login_required
def invitation_action(request):
    invitation_pk = request.POST.get('invitation_pk')
    invitation = get_object_or_404(Invitation, pk=invitation_pk)
    if request.method == 'POST':
        if invitation.invited_by != request.user:
            raise PermissionDenied()
        if 'withdraw' in request.POST:
            invitation.delete()
            messages.success(request, _('Invitation was withdrawn.'))
        elif 'resend' in request.POST:
            bucket = get_invitation_bucket(request.user, _('invitation mails'))
            try:
                bucket.consume(1)
            except bucket.TokensExceeded as e:
                messages.error(request, e.get_message())
            else:
                invitation.send_email()
                messages.success(request, _('Invitation mail was resent.'))
    return redirect('guests_index')

@login_required
def show_invited_by(request):
    if not request.user.is_guest:
        return redirect('guests_index')

    guest = Guest.objects.get(guest_user=request.user)
    return render(request, 'guests/invited_by.html', {
        'guest': guest
    })

def accept(request, invitation_token):
    if request.user.is_authenticated():
        return redirect('guests_index')

    try:
        invitation_pk = signing.loads(invitation_token)
    except signing.BadSignature:
        raise PermissionDenied

    try:
        invitation = Invitation.objects.get(pk=invitation_pk)
    except Invitation.DoesNotExist:
        return render(request, 'guests/invitation_withdrawn.html')

    if Mafiasi.objects.filter(username=invitation.username+'.guest').count():
        return render(request, 'guests/username_exists.html', {
            'username': invitation.username,
        })

    try:
        existing_account = Mafiasi.objects.get(email=invitation.email)
        return render(request, 'guests/has_account.html', {
            'existing_account': existing_account
        })
    except Mafiasi.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            mafiasi = invitation.accept_with_password(password)
            mafiasi.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, mafiasi)
            return redirect('guests_invited_by')
    else:
        form = PasswordForm()

    return render(request, 'guests/accept.html', {
        'invitation': invitation,
        'form': form,
        'guest_extension': settings.GUEST_EXTENTION,
    })
