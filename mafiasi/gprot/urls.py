from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', index, name='gprot_index'),
    url(r'^view/(\d+)$', view_gprot, name='gprot_view'),
    url(r'^create$', create_gprot, name='gprot_create'),
    url(r'^list_own$', list_own_gprots, name='gprot_list_own'),
    url(r'^edit/(\d+)$', edit_gprot, name='gprot_edit'),
    url(r'^edit/(\d+)/metadata$', edit_metadata, name='gprot_edit_metadata'),
    url(r'^attach/(\d+)$', create_attachment, name='attachment_create'),
    url(r'^publish/(\d+)$', publish_gprot, name='gprot_publish'),
    url(r'^delete/(\d+)$', delete_gprot, name='gprot_delete'),
    url(r'^forget/(\d+)$', forget_owner, name='gprot_forget_owner'),
    url(r'^notifications/$', notifications, name='gprot_notifications'),
    url(r'^notifications/delete/(\d+)$', delete_notification,
        name='gprot_notification_delete'),
    url(r'^reminders/$', reminders, name='gprot_reminders'),
    url(r'^reminders/delete/(\d+)$', delete_reminder,
        name='gprot_reminder_delete'),
    url(r'^favorite/$', favorite),
]
