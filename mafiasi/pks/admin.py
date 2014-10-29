from django.contrib import admin

from mafiasi.pks.models import AssignedKey, KeysigningParty, Participant, PGPKey

admin.site.register(AssignedKey)
admin.site.register(KeysigningParty)
admin.site.register(Participant)
admin.site.register(PGPKey)
