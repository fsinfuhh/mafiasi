from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.urls import path, re_path

from .views import *

urlpatterns = [
    path("change_email/<token>", change_email, name="registration_change_email"),
    path("request_successful", request_successful, name="registration_request_successful"),
    path("account", account_settings, name="registration_account"),
]

if settings.REGISTER_ENABLED:
    urlpatterns += [
        path("request_account", request_account, name="registration_request_account"),
        path("additional_info", additional_info, name="registration_additional_info"),
        path("create_account/<info_token>", create_account, name="registration_create_account"),
    ]
