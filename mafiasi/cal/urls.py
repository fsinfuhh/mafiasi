from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.cal.views',
    url(r'^$', 'index', name='cal_index'),
    url(r'^calendar_data$', 'calendar_data', name='cal_calendar_data'),
)
