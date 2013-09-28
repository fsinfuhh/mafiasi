from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.wiki.views',
    url(r'^autocomplete$', 'autocomplete', name='wiki_autocomplete'),
)
