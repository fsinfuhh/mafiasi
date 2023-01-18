from django.contrib import admin

from mafiasi.mailinglist.models import (
    Mailinglist,
    ModeratedMail,
    RefusedRecipient,
    WhitelistedAddress,
)

admin.site.register(Mailinglist)
admin.site.register(WhitelistedAddress)
admin.site.register(RefusedRecipient)
admin.site.register(ModeratedMail)
