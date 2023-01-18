from django.conf import settings
from django.urls import path
from django.views.generic.base import RedirectView

include_at_top = True

urlpatterns = [
    path(".well-known/carddav", RedirectView.as_view(url=settings.SOGO_URL + "/.well-known/carddav"), name="carddav"),
    path(".well-known/caldav", RedirectView.as_view(url=settings.SOGO_URL + "/.well-known/caldav"), name="caldav"),
]
