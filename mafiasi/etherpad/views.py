from mafiasi.etherpad.etherpad import Etherpad

from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.conf import settings

from urllib2 import URLError


class NewEtherpadForm(forms.Form):
    name = forms.RegexField(max_length=30, regex="[a-zA-Z0-9\-_]+")

    def __init__(self, user, *args, **kwargs):
        super(NewEtherpadForm, self).__init__(*args, ** kwargs)
        self.fields['Group'] = forms.ModelChoiceField(queryset=Group.objects.filter(mafiasi=user))

    class Meta:
        model = Group

def index(request):
    pad_list={}
    if request.user.is_authenticated():
        ep = Etherpad()
        for group in request.user.groups.all():
            print group
            pads = ep.get_group_pads(group.name)
            pad_list[group.name] = []
            for pad in pads:
                pad_list[group.name].append(pad.split('$')[1])
    return TemplateResponse(request, 'etherpad/index.html', {
                'pad_list': pad_list,
                'login': request.user.is_authenticated(),
                })

@login_required
def create_new_pad(request):
    if request.method == 'POST':
        form = NewEtherpadForm(request.user, request.POST)
        if form.is_valid():
            group = form.cleaned_data['Group']
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
    # testen obs die Gruppe gibt
    group = get_object_or_404(Group, name=group_name)
    # Testen ob der User überhaupt an die Gruppe darf
    if not Group.objects.filter(id = group.id, mafiasi=request.user):
        return TemplateResponse(request, 'etherpad/forbidden.html', {
                    'group_name': group_name,
                    }, status=403)

    ep = Etherpad()
    try:
        ep.create_session(request.user, group_name)
        groupID = ep.get_group_id(group_name)
        padURL = '%s://%s/p/%s$%s' % (
                settings.ETHERPAD_PROTOCOLL,
                settings.ETHERPAD_DOMAIN,
                groupID,
                pad_name)
        cookie = ep.get_session_cookie(request.user)
    except URLError:
        # etherpad server war nicht erreichbar
        return TemplateResponse(request, 'etherpad/server_error.html', {
            }, status=500)

    response = TemplateResponse(request, 'etherpad/pad.html', {
        'padURL':padURL,
    })
    response.set_cookie('epSession', cookie, domain=settings.ETHERPAD_DOMAIN)
    return response

