from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.mumble.views',
    url(r'^$', 'index', name='mumble_index'),
    url(r'^create$', 'create', name='mumble_create'),
    url(r'^password_reset$', 'password_reset', name='mumble_password_reset'),
)
