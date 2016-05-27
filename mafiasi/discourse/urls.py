from django.conf.urls import url

from .views import sso

urlpatterns = [
    url(r'^sso$', sso, name='discourse_sso'),
]
