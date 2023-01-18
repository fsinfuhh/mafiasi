from django import forms
from django.contrib import admin

from mafiasi.base.models import Yeargroup
from mafiasi.jabber.models import (
    DefaultGroup,
    JabberUserMapping,
    YeargroupSrGroupMapping,
)


class YeargroupSrGroupMappingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        yeargroups = Yeargroup.objects.values_list("id", "name")
        self.fields["yeargroup_id"] = forms.ChoiceField(choices=yeargroups)


class YeargroupSrGroupMappingAdmin(admin.ModelAdmin):
    form = YeargroupSrGroupMappingForm


admin.site.register(DefaultGroup)
admin.site.register(JabberUserMapping)
admin.site.register(YeargroupSrGroupMapping, YeargroupSrGroupMappingAdmin)
