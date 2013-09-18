from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.registration.views',
    url(r'^request_account$', 'request_account',
            name='registration_request_account'),
    url(r'^create_account/([a-zA-Z0-9:_-]+)$', 'create_account',
            name='registration_create_account'),
    url(r'^request_successful/([a-z0-9.]+)$', 'request_successful',
            name='registration_request_successful'),
)
