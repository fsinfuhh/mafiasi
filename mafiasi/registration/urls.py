from django.urls import path, re_path
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import *


urlpatterns = [
    path('change_email/<token>', change_email,
            name='registration_change_email'),
    path('request_successful', request_successful,
            name='registration_request_successful'),
    path('account', account_settings, name='registration_account'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), {
        'password_reset_form': PasswordResetForm
    }, name='password_reset'),
    path('password_reset/done', auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='django.contrib.auth.views.password_reset_confirm'),
    path('password_reset/complete', auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete')
]

if settings.REGISTER_ENABLED:
    urlpatterns += [
        path('request_account', request_account,
                name='registration_request_account'),
        path('additional_info', additional_info,
                name='registration_additional_info'),
        path('create_account/<info_token>', create_account,
                name='registration_create_account'),
    ]
