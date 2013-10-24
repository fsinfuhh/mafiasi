from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.ksp.views',
    url(r'^$', 'index', name='ksp_index'),
)
