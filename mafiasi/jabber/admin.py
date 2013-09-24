from django.contrib import admin

from mafiasi.jabber.models import (DefaultGroup, JabberUserMapping,
        YeargroupSrGroupMapping)

admin.site.register(DefaultGroup)
admin.site.register(JabberUserMapping)
admin.site.register(YeargroupSrGroupMapping)
