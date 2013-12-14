from django.contrib import admin

from mafiasi.groups.models import GroupInvitation, GroupProperties

admin.site.register(GroupInvitation)
admin.site.register(GroupProperties)
