from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.etherpad.views',
    url(r'^$', 'index', name='ep_index'),
    url(r'^create_new_pad$', 'create_new_pad', name='ep_create_new_pad'),
    url(r'^pad/([A-Za-z0-9\-_]+)/([A-Za-z0-9\-_]+)$', 'show_pad', name='ep_show_pad'),
)
