from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.cal.views',
    url(r'^$', 'index', name='cal_davindex'),
    url(r'^([A-Za-z0-9_.-]+)/$', 'proxy_request_collection',
            name='cal_proxy_request_collection'),
    url(r'^([A-Za-z0-9_.-]+)/([a-zA-Z0-9_-]+)\.(ics|vcf)/(.*)', 'proxy_request',
            name='cal_proxy_request'),
)
