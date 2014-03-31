from django.contrib import admin

from mafiasi.gprot.models import GProt, GProtNotification, Reminder

admin.site.register(GProt)
admin.site.register(GProtNotification)
admin.site.register(Reminder)
