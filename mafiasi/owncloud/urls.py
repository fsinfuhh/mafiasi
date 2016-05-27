from django.conf.urls import url

from .views import set_quota

urlpatterns = [
    url(r'^set_quota/([a-z0-9.]+)$', set_quota, name='owncloud_set_quota'),
]
