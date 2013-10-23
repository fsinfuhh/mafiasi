from django.contrib import admin

from mafiasi.cal.models import DavObject, DavObjectPermission, ShownCalendar

admin.site.register(DavObject)
admin.site.register(DavObjectPermission)
admin.site.register(ShownCalendar)
