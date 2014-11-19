from __future__ import unicode_literals

from mafiasi.etherpad.etherpad import Etherpad

from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.conf import settings

from urllib2 import URLError

import datetime

class NewEtherpadForm(forms.Form):
    name = forms.RegexField(max_length=30, regex="[a-zA-Z0-9\-_]+")

    def __init__(self, user, *args, **kwargs):
        super(NewEtherpadForm, self).__init__(*args, **kwargs)
        self.fields['group'] = forms.ModelChoiceField(queryset=user.groups)

class DeleteEtherpadForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(DeleteEtherpadForm, self).__init__(*args, **kwargs)

def index(request):
    pad_list={}
    groups_admin={}
    if request.user.is_authenticated():
        ep = Etherpad()
        for group in request.user.groups.all():
            pads = ep.get_group_pads(group.name)
            is_admin = False
            if group.properties.admins.filter(pk=request.user.pk).exists():
                is_admin = True
            pad_list[group.name] = []
            for pad in pads:
                edit_time = ep.get_last_edit(pad)
                edit_time_out = datetime.datetime.fromtimestamp(edit_time)
                edit_time_not_old = True
                if edit_time_out < datetime.datetime.now() - datetime.timedelta(days=7):
                    edit_time_not_old = False
                pad_list[group.name].append(
                    {
                        "name": pad.split('$')[1],
                        "admin": is_admin,
                        "last_edit": edit_time_out,
                        "edit_time_not_old": edit_time_not_old
                    })
    return TemplateResponse(request, 'etherpad/index.html', {
        'pad_list': pad_list,
        'groups_admin':groups_admin,
        'etherpad_link': settings.SERVICE_LINKS['etherpad']
    })

@login_required
def create_new_pad(request):
    if request.method == 'POST':
        form = NewEtherpadForm(request.user, request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            name = form.cleaned_data['name']
            ep = Etherpad()
            ep.create_group_pad(group.name, name)
            return redirect('ep_show_pad', group, name)
    else:
        form = NewEtherpadForm(request.user)
    return TemplateResponse(request, 'etherpad/create_new_pad.html', {
        'form': form,
    })

@login_required
def delete_pad(request, group_name, pad_name):
    # test if user is in group
    if not request.user.groups.filter(name=group_name).exists():
        return TemplateResponse(request, 'etherpad/forbidden.html', {
            'group_name': group_name,
        }, status=403)
    # test if user is admin in the group
    group = request.user.groups.filter(name=group_name).all()[0]
    if not group.properties.admins.filter(pk=request.user.pk):
        return TemplateResponse(request, 'etherpad/forbidden.html', {
            'group_name': group_name,
        }, status=403)

    if request.method == 'POST':
        form = DeleteEtherpadForm(request.user, request.POST)
        if form.is_valid():
            ep = Etherpad()
            ep.delete_pad('{0}${1}'.format(
                ep.get_group_id(group_name),
                pad_name))
            return redirect('ep_index')

    form = DeleteEtherpadForm(request.user)
    return TemplateResponse(request, 'etherpad/delete_pad.html', {
        'form': form,
        'group': group_name,
        'pad': pad_name,
    })

@login_required
def show_pad(request, group_name, pad_name):
    # test if user is in group
    if not request.user.groups.filter(name=group_name).exists():
        return TemplateResponse(request, 'etherpad/forbidden.html', {
            'group_name': group_name,
        }, status=403)

    ep = Etherpad()
    try:
        ep.create_session(request.user, group_name)
        group_id = ep.get_group_id(group_name)
        pad_url = '{0}/p/{1}${2}'.format(
                settings.ETHERPAD_URL,
                group_id,
                pad_name)
        cookie = ep.get_session_cookie(request.user)
    except URLError:
        return TemplateResponse(request, 'etherpad/server_error.html', {
            }, status=500)

    is_fullscreen = 'fullscreen' in request.GET
    response = TemplateResponse(request, 'etherpad/pad.html', {
        'pad_url': pad_url,
        'group_name': group_name,
        'pad_name': pad_name,
        'fullscreen': is_fullscreen,
        'base_template': 'base_raw.html' if is_fullscreen else 'base.html'
    })
    cookie_domain = '.' + request.get_host()
    response.set_cookie('sessionID', cookie, domain=cookie_domain)
    return response

def show_pad_html(request, group_name, pad_name):
    # test if user is in group
    if not request.user.groups.filter(name=group_name).exists():
        return TemplateResponse(request, 'etherpad/forbidden.html', {
            'group_name': group_name,
        }, status=403)

    ep = Etherpad()
    full_pad_name = '{0}${1}'.format(
                ep.get_group_id(group_name),
                pad_name)
    html = ep.get_html(full_pad_name)
    return TemplateResponse(request, 'etherpad/pad_html.html', {
        'html': html[27:-14], #  strip <html> and head
        'pad_name': pad_name,
        'group_name': group_name
    })

