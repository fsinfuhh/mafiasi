from django.conf.urls import url
from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import *


urlpatterns = [
    url(r'^change_email/([a-zA-Z0-9:_-]+)$', change_email,
            name='registration_change_email'),
    url(r'^request_successful$', request_successful,
            name='registration_request_successful'),
    url(r'^account$', account_settings, name='registration_account'),

    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(), {
        'password_reset_form': PasswordResetForm
    }, name='password_reset'),
    url(r'^password_reset/done$', auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='django.contrib.auth.views.password_reset_confirm'),
    url(r'^password_reset/complete', auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete')
]

if settings.REGISTER_ENABLED:
    urlpatterns += [
        url(r'^request_account$', request_account,
                name='registration_request_account'),
        url(r'^additional_info$', additional_info,
                name='registration_additional_info'),
        url(r'^create_account/([a-zA-Z0-9:_-]+)$', create_account,
                name='registration_create_account'),
    ]
