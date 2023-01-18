from django.urls import path

from .views import mailaddresses

urlpatterns = [
    path("mailaddresses", mailaddresses, name="mail_mailaddesses"),
]
