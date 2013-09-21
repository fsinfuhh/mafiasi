from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.mumble.views',
    url(r'^$', 'index', name='mumble_index'),
)
