from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from mafiasi.groups.models import Group, GroupProxy
from mafiasi.mailinglist.models import Mailinglist, ModeratedMail
from mafiasi.mailinglist.forms import AddWhitelistForm, SettingsForm

@login_required
def show_list(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    group_proxy = GroupProxy(group)
    if not group_proxy.is_member(request.user):
        raise PermissionDenied()

    try:
        mailinglist = Mailinglist.objects.get(group=group)
        moderated_mails = mailinglist.moderated_mails.all()
        whitelist_count = mailinglist.whitelist_addresses.count()
    except Mailinglist.DoesNotExist:
        mailinglist = None
        moderated_mails = []
        whitelist_count = 0

    is_admin = GroupProxy(group).is_admin(request.user)
    return render(request, 'mailinglist/show_list.html', {
        'group': group,
        'mailinglist': mailinglist,
        'moderated_mails': moderated_mails,
        'whitelist_count': whitelist_count,
        'is_admin': is_admin
    })

@login_required
def create_list(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if not GroupProxy(group).is_admin(request.user):
        raise PermissionDenied()
    if request.method == 'POST':
        mailinglist, created = Mailinglist.objects.get_or_create(group=group)
        if created:
            msg = _('Mailinglist {list_name} was created.').format(
                    list_name=group.name)
            messages.success(request, msg)
    return redirect('mailinglist_show_list', group.name)

@login_required
def mailaction(request, group_name, mmail_pk):
    group = get_object_or_404(Group, name=group_name)
    if not GroupProxy(group).is_admin(request.user):
        raise PermissionDenied()
    try:
        mailinglist = Mailinglist.objects.get(group=group)
    except Mailinglist.DoesNotExist:
        return redirect('mailinglist_show_list', group.name)

    try:
        mmail = ModeratedMail.objects.get(pk=mmail_pk, mailinglist=mailinglist)
    except ModeratedMail.DoesNotExist:
        return redirect('mailinglist_show_list', group.name)

    if request.method == 'POST':
        if 'allow' in request.POST:
            mmail.unmoderate()
            messages.success(request, _('Mail was sent to mailinglist.'))
        elif 'discard' in request.POST:
            messages.success(request, _('Mail was discarded.'))
            mmail.delete()

    return redirect('mailinglist_show_list', group.name)

@login_required
def manage_whitelist(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    group_proxy = GroupProxy(group)
    if not group_proxy.is_member(request.user):
        raise PermissionDenied()
    is_admin = group_proxy.is_admin(request.user)
    try:
        mailinglist = Mailinglist.objects.get(group=group)
    except Mailinglist.DoesNotExist:
        return redirect('mailinglist_show_list', group.name)

    if 'add' in request.POST and is_admin:
        add_form = AddWhitelistForm(request.POST, mailinglist=mailinglist)
        if add_form.is_valid():
            add_form.save()
            return redirect('mailinglist_whitelist', group.name)
    else:
        add_form = AddWhitelistForm(mailinglist=mailinglist)

    if 'delete' in request.POST and is_admin:
        address_pk = request.POST.get('address_pk', 0)
        mailinglist.whitelist_addresses.filter(pk=address_pk).delete()
        return redirect('mailinglist_whitelist', group.name)

    entries = mailinglist.whitelist_addresses.order_by('email')

    return render(request, 'mailinglist/whitelist.html', {
        'mailinglist': mailinglist,
        'entries': entries,
        'add_form': add_form,
        'is_admin': is_admin
    })

@login_required
def manage_settings(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if not GroupProxy(group).is_admin(request.user):
        raise PermissionDenied()
    
    try:
        mailinglist = Mailinglist.objects.get(group=group)
    except Mailinglist.DoesNotExist:
        return redirect('mailinglist_show_list', group.name)
    
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=mailinglist)
        if form.is_valid():
            form.save()
            messages.success(request, _('Mailinglist settings saved.'))
            return redirect('mailinglist_show_list', group.name)
    else:
        form = SettingsForm(instance=mailinglist)

    return render(request, 'mailinglist/settings.html', {
        'mailinglist': mailinglist,
        'form': form
    })
