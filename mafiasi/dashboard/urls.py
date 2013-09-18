from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.dashboard.views',
    url(r'^$', 'index', name='dashboard_index'),
)
