from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='gprot_index'),
    path('view/<int:gprot_pk>', view_gprot, name='gprot_view'),
    path('create', create_gprot, name='gprot_create'),
    path('list_own', list_own_gprots, name='gprot_list_own'),
    path('edit/<int:gprot_pk>', edit_gprot, name='gprot_edit'),
    path('edit/<int:gprot_pk>/metadata', edit_metadata, name='gprot_edit_metadata'),
    path('attach/<int:gprot_pk>', create_attachment, name='attachment_create'),
    path('publish/<int:gprot_pk>', publish_gprot, name='gprot_publish'),
    path('delete/<int:gprot_pk>', delete_gprot, name='gprot_delete'),
    path('forget/(<int:gprot_pk>', forget_owner, name='gprot_forget_owner'),
    path('notifications/', notifications, name='gprot_notifications'),
    path('notifications/delete/<int:notification_pk>', delete_notification,
        name='gprot_notification_delete'),
    path('reminders/', reminders, name='gprot_reminders'),
    path('reminders/delete/<int:reminder_pk>', delete_reminder,
        name='gprot_reminder_delete'),
    path('favorite/', favorite),
]
