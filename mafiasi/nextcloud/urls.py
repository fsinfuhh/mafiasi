from django.urls import path

from .views import set_quota

urlpatterns = [
    path("set_quota/<slug:username>", set_quota, name="nextcloud_set_quota"),
]
