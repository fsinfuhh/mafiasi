from django.conf.urls import url
from django.views.generic.base import RedirectView

include_at_top = True

urlpatterns = [
    url(r'.well-known/carddav', RedirectView.as_view(url='https://sogo.mafiasi.de/.well-known/carddav'), name='carddav'),
    url(r'.well-known/caldav', RedirectView.as_view(url='https://sogo.mafiasi.de/.well-known/caldav'), name='caldav'),
]
