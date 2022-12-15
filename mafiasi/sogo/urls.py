from django.conf.urls import url
from django.conf import settings
from django.views.generic.base import RedirectView

include_at_top = True

urlpatterns = [
    url(r'.well-known/carddav', RedirectView.as_view(url=settings.SOGO_URL + '/.well-known/carddav'), name='carddav'),
    url(r'.well-known/caldav', RedirectView.as_view(url=settings.SOGO_URL + '/.well-known/caldav'), name='caldav'),
]
