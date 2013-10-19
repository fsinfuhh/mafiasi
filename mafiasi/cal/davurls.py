from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.cal.views',
    url(r'^$', 'index', name='cal_davindex'),
    url(r'^([^/]+)/([a-zA-Z0-9_-]+).ics', 'proxy_calendar',
            name='cal_proxy_calendar'),
    url(r'^([^/]+)/([a-zA-Z0-9_-]+).vcf', 'proxy_contactlist',
            name='cal_proxy_contactlist'),
)
