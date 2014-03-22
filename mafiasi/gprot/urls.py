from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.gprot.views',
    url(r'^$', 'index', name='gprot_index'),
    url(r'^view/(\d+)$', 'view_gprot', name='gprot_view'),
    url(r'^create$', 'create_gprot', name='gprot_create'),
    url(r'^list_own$', 'list_own_gprots', name='gprot_list_own'),
    url(r'^edit/(\d+)$', 'edit_gprot', name='gprot_edit'),
    url(r'^publish/(\d+)$', 'publish_gprot', name='gprot_publish'),
    url(r'^notifications/$', 'notifications', name='gprot_notifications'),
    url(r'^notifications/delete/(\d+)$', 'delete_notification',
        name='gprot_notification_delete')
)
