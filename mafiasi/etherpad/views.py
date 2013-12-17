from mafiasi.etherpad.etherpad import Etherpad

from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.conf import settings

from urllib2 import URLError


class NewEtherpadForm(forms.Form):
    name = forms.RegexField(max_length=30, regex="[a-zA-Z0-9\-_]+")

    def __init__(self, user, *args, **kwargs):
        super(NewEtherpadForm, self).__init__(*args, **kwargs)
        self.fields['group'] = forms.ModelChoiceField(queryset=user.groups)

def index(request):
    pad_list={}
    if request.user.is_authenticated():
        ep = Etherpad()
        for group in request.user.groups.all():
            pads = ep.get_group_pads(group.name)
            pad_list[group.name] = []
            for pad in pads:
                pad_list[group.name].append(pad.split('$')[1])
    return TemplateResponse(request, 'etherpad/index.html', {
        'pad_list': pad_list,
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
        pad_url = '{0}://{1}/p/{2}${3}'.format(
                settings.ETHERPAD_PROTOCOL,
                settings.ETHERPAD_DOMAIN,
                group_id,
                pad_name)
        cookie = ep.get_session_cookie(request.user)
    except URLError:
        return TemplateResponse(request, 'etherpad/server_error.html', {
            }, status=500)
    
    is_fullscreen = 'fullscreen' in request.GET
    response = TemplateResponse(request, 'etherpad/pad.html', {
        'pad_url':pad_url,
        'group_name': group_name,
        'pad_name': pad_name,
        'fullscreen': is_fullscreen,
        'base_template': 'base_raw.html' if is_fullscreen else 'base.html'
    })
    response.set_cookie('epSession', cookie, domain=settings.ETHERPAD_DOMAIN)
    return response

