import datetime
from operator import itemgetter
from urllib.error import URLError

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from mafiasi.etherpad.dbview import get_group_pads
from mafiasi.etherpad.etherpad import Etherpad
from mafiasi.etherpad.models import PinnedEtherpad
from mafiasi.groups.models import GroupProxy


class NewEtherpadForm(forms.Form):
    name = forms.RegexField(max_length=30, regex="[a-zA-Z0-9\-_]+")

    def __init__(self, user, *args, **kwargs):
        super(NewEtherpadForm, self).__init__(*args, **kwargs)
        self.fields["group"] = forms.ModelChoiceField(queryset=user.groups)


class DeleteEtherpadForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(DeleteEtherpadForm, self).__init__(*args, **kwargs)


def index(request):
    group_pad_list = []
    pinned_pads = None
    if request.user.is_authenticated:
        pad_dict = {}
        groups = request.user.groups.all().order_by("name")
        group_names = [group.name for group in groups]
        pad_dict = get_group_pads(group_names)
        old_time = datetime.datetime.now() - datetime.timedelta(days=7)
        for group in groups:
            is_admin = GroupProxy(group).is_admin(request.user)
            pads = pad_dict[group.name]
            for pad in pads:
                edit_time = datetime.datetime.fromtimestamp(pad["timestamp"])
                edit_time_not_old = edit_time >= old_time
                pad["admin"] = is_admin
                pad["last_edit"] = edit_time
                pad["edit_time_not_old"] = edit_time_not_old
            pads.sort(key=itemgetter("last_edit"), reverse=True)
            group_pad_list.append({"group_name": group.name, "pads": pads})
        pinned_pads = PinnedEtherpad.objects.filter(user=request.user).order_by("pad_name")

    return TemplateResponse(
        request,
        "etherpad/index.html",
        {
            "pinned_pads": pinned_pads,
            "group_pad_list": group_pad_list,
            "etherpad_link": settings.ETHERPAD_URL,
        },
    )


@login_required
def create_new_pad(request):
    if request.method == "POST":
        form = NewEtherpadForm(request.user, request.POST)
        if form.is_valid():
            group = form.cleaned_data["group"]
            name = form.cleaned_data["name"]
            ep = Etherpad()
            ep.create_group_pad(group.name, name)
            return redirect("ep_show_pad", group, name)
    else:
        form = NewEtherpadForm(request.user)
    return TemplateResponse(
        request,
        "etherpad/create_new_pad.html",
        {
            "form": form,
        },
    )


@login_required
def delete_pad(request, group_name, pad_name):
    # test if user is in group
    if not request.user.groups.filter(name=group_name).exists():
        return TemplateResponse(
            request,
            "etherpad/forbidden-notingroup.html",
            {
                "group_name": group_name,
            },
            status=403,
        )
    # test if user is admin in the group
    group = request.user.groups.filter(name=group_name).all()[0]
    if not group.properties.admins.filter(pk=request.user.pk):
        return TemplateResponse(
            request,
            "etherpad/forbidden-notadmin.html",
            {
                "group_name": group_name,
            },
            status=403,
        )

    if request.method == "POST":
        form = DeleteEtherpadForm(request.user, request.POST)
        if form.is_valid():
            ep = Etherpad()
            ep.delete_pad("{0}${1}".format(ep.get_group_id(group_name), pad_name))

            # delete pinned pads
            PinnedEtherpad.objects.filter(group_name=group, pad_name=pad_name).delete()

            return redirect("ep_index")

    form = DeleteEtherpadForm(request.user)
    return TemplateResponse(
        request,
        "etherpad/delete_pad.html",
        {
            "form": form,
            "group": group_name,
            "pad": pad_name,
        },
    )


@login_required
@require_POST
def pin_pad(request, group_name, pad_name):
    try:
        group = request.user.groups.get(name=group_name)
    except ObjectDoesNotExist:
        return TemplateResponse(
            request,
            "etherpad/forbidden-notingroup.html",
            {
                "group_name": group_name,
            },
            status=403,
        )

    # ensure that pad exists
    ep = Etherpad()
    full_pad_name = "{0}${1}".format(ep.get_group_id(group_name), pad_name)
    html = ep.get_html(full_pad_name)

    PinnedEtherpad.objects.get_or_create(user=request.user, group_name=group, pad_name=pad_name)

    return redirect("ep_index")


@login_required
@require_POST
def unpin_pad(request, group_name, pad_name):
    try:
        group = Group.objects.get(name=group_name)
        PinnedEtherpad.objects.filter(user=request.user, group_name=group, pad_name=pad_name).delete()
    except ObjectDoesNotExist:
        pass
    # redirect to pad overview
    return redirect("ep_index")


@login_required
def show_pad(request, group_name, pad_name):
    # test if user is in group
    if not request.user.groups.filter(name=group_name).exists():
        return TemplateResponse(
            request,
            "etherpad/forbidden-notingroup.html",
            {
                "group_name": group_name,
            },
            status=403,
        )

    ep = Etherpad()
    try:
        ep.create_session(request.user, group_name)
        group_id = ep.get_group_id(group_name)
        pad_url = "{0}/p/{1}${2}".format(settings.ETHERPAD_URL, group_id, pad_name.replace("/", "_"))
        cookie = ep.get_session_cookie(request.user)
    except URLError:
        return TemplateResponse(request, "etherpad/server_error.html", {}, status=500)

    is_fullscreen = "fullscreen" in request.GET
    response = TemplateResponse(
        request,
        "etherpad/pad.html",
        {
            "pad_url": pad_url,
            "group_name": group_name,
            "pad_name": pad_name,
            "fullscreen": is_fullscreen,
            "base_template": "base_raw.html" if is_fullscreen else "base.html",
        },
    )
    cookie_domain = settings.EP_COOKIE_DOMAIN
    response.set_cookie("sessionID", cookie, domain=cookie_domain)
    response["Access-Control-Allow-Origin"] = "https://ep.mafiasi.de"
    return response


def show_pad_html(request, group_name, pad_name):
    # test if user is in group
    if not request.user.groups.filter(name=group_name).exists():
        return TemplateResponse(
            request,
            "etherpad/forbidden-notingroup.html",
            {
                "group_name": group_name,
            },
            status=403,
        )

    ep = Etherpad()
    full_pad_name = "{0}${1}".format(ep.get_group_id(group_name), pad_name.replace("/", "_"))
    html = ep.get_html(full_pad_name)
    return TemplateResponse(
        request,
        "etherpad/pad_html.html",
        {"html": html[27:-14], "pad_name": pad_name, "group_name": group_name},  #  strip <html> and head
    )
