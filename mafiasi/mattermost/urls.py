from django.conf.urls import url

from .views import get_user_info

urlpatterns = [
    url(r'^user$', get_user_info, name='mattermost_get_user_info'),
]
