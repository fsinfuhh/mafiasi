from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.cal.views',
    url(r'^$', 'index', name='cal_index'),
)
