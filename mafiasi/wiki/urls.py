from django.conf.urls import url

from . import views

include_at_top = True

urlpatterns = [
    url(r'wiki/autocomplete$', views.autocomplete, name='wiki_autocomplete'),
    url(r'(?P<search>.*)', views.redirect_to_wiki, name='wiki_redirect')
]
