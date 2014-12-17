from django.conf.urls import patterns, url

from mafiasi.registration.forms import PasswordResetForm

urlpatterns = patterns('mafiasi.registration.views',
    url(r'^request_account$', 'request_account',
            name='registration_request_account'),
    url(r'^additional_info$', 'additional_info',
            name='registration_additional_info'),
    url(r'^create_account/([a-zA-Z0-9:_-]+)$', 'create_account',
            name='registration_create_account'),
    url(r'^request_successful/([a-z0-9.\-_]+@[a-z0-9.\-_]+)$', 'request_successful',
            name='registration_request_successful'),
    url(r'^account$', 'account_settings', name='registration_account'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^password_reset/$', 'password_reset', {
        'password_reset_form': PasswordResetForm
    }, name='password_reset'),
    url(r'^password_reset/done$', 'password_reset_done',
            name='password_reset_done'),
    url(r'^password_reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)$',
            'password_reset_confirm', name='password_reset_confirm'),
    url(r'^password_reset/complete', 'password_reset_complete',
            name='password_reset_complete')
)
