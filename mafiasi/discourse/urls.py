from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.discourse.views',
    url(r'^sso$', 'sso', name='discourse_sso'),
)