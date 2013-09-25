from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.base.views',
    url(r'^inprint$', 'inprint', name='base_inprint'),
    url(r'^technical_info$', 'technical_info', name='base_technical_info'),
    url(r'^problems$', 'problems', name='base_problems'),
)
