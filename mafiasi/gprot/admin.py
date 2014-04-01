from django.contrib import admin

from mafiasi.gprot.models import GProt, Notification, Reminder

admin.site.register(GProt)
admin.site.register(Notification)
admin.site.register(Reminder)
