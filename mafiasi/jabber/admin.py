from django.contrib import admin

from mafiasi.jabber.models import (PrivacyDefaultList, PrivacyList,
        PrivacyListData, PrivateStorage, Rostergroups, Rosteruser,
        SrGroup, SrUser, JabberUser, Vcard, JabberUserMapping,
        YeargroupSrGroupMapping)

admin.site.register(PrivacyDefaultList)
admin.site.register(PrivacyList)
admin.site.register(PrivacyListData)
admin.site.register(PrivateStorage)
admin.site.register(Rostergroups)
admin.site.register(Rosteruser)
admin.site.register(SrGroup)
admin.site.register(SrUser)
admin.site.register(JabberUser)
admin.site.register(Vcard)
admin.site.register(JabberUserMapping)
admin.site.register(YeargroupSrGroupMapping)
