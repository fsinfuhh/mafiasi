from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.registration.views',
    url(r'^request_account$', 'request_account',
            name='registration_request_account'),
    url(r'^create_account/([a-zA-Z0-9:_-]+)$', 'create_account',
            name='registration_create_account'),
    url(r'^request_successful/([a-z0-9.]+)$', 'request_successful',
            name='registration_request_successful'),
    url(r'^account$', 'account_settings', name='registration_account'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^password_reset/$', 'password_reset', name='password_reset'),
    url(r'^password_reset/done$', 'password_reset_done',
            name='password_reset_done'),
    url(r'^password_reset/confirm/(?P<uidb36>[a-zA-Z0-9-]+)/(?P<token>[a-zA-Z0-9-]+)$',
            'password_reset_confirm', name='password_reset_confirm'),
    url(r'^password_reset/complete', 'password_reset_complete',
            name='password_reset_complete')
)

