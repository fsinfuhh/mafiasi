from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.mailinglist.views',
    url(r'^([a-zA-Z0-9-]+)/$', 'show_list', name='mailinglist_show_list'),
    url(r'^([a-zA-Z0-9-]+)/create$', 'create_list',
            name='mailinglist_create_list'),
    url(r'^([a-zA-Z0-9-]+)/mailaction/(\d+)$', 'mailaction',
            name='mailinglist_mailaction'),
    url(r'^([a-zA-Z0-9-]+)/whitelist', 'manage_whitelist',
            name='mailinglist_whitelist'),
)
