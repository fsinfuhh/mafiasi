from django.contrib import admin

from mafiasi.cal.models import DavObject, DavObjectPermission

admin.site.register(DavObject)
admin.site.register(DavObjectPermission)
