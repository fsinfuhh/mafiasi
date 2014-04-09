from django.contrib import admin

from mafiasi.gprot.models import Attachment, GProt, Notification, Reminder

admin.site.register(Attachment)
admin.site.register(GProt)
admin.site.register(Notification)
admin.site.register(Reminder)
