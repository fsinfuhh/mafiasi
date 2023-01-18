import re

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render

from mafiasi.base.models import LdapUser

QUOTA_RE = re.compile("^\d+(GB|MB)$")


class SetQuotaForm(forms.Form):
    quota = forms.CharField()

    def clean_quota(self):
        if not QUOTA_RE.match(self.cleaned_data["quota"]):
            raise forms.ValidationError("Invalid quota")
        return self.cleaned_data["quota"]


@permission_required("nextcloud.set_quota")
def set_quota(request, username):
    try:
        user = LdapUser.lookup(username)
    except LdapUser.DoesNotExist:
        return HttpResponseNotFound("User not found")

    if request.method == "POST":
        form = SetQuotaForm(request.POST)
        if form.is_valid():
            user.nextcloud_quota = form.cleaned_data["quota"]
            user.save()
            messages.success(request, "Quota sucessfully set.")
            return redirect("nextcloud_set_quota", username)
    else:
        form = SetQuotaForm(initial={"quota": user.nextcloud_quota if user.nextcloud_quota else ""})

    return render(request, "nextcloud/set_quota.html", {"username": username, "form": form})
