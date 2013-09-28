from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.jabber.views',
    url(r'^$', 'index', name='jabber_index'),
    url(r'^create$', 'create', name='jabber_create'),
)
