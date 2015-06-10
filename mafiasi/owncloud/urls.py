from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.owncloud.views',
    url(r'^set_quota/([a-z0-9.]+)$', 'set_quota', name='owncloud_set_quota'),
)
