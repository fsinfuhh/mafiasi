from django.conf.urls import url

from .views import mailaddresses

urlpatterns = [
    url(r'^mailaddresses$', mailaddresses, name='mail_mailaddesses'),
]
