from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.dashboard.views',
    url(r'^$', 'index', name='dashboard_index'),
    url(r'^news/(\d+)$', 'show_news', name='dashboard_show_news'),
)
