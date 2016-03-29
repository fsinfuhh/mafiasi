from django.conf.urls import url

from .views import index, create

urlpatterns = [
    url(r'^$', index, name='jabber_index'),
    url(r'^create$', create, name='jabber_create'),
]
