from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.mail.views',
    url(r'^mailaddresses$', 'mailaddresses', name='mail_mailaddesses'),
)
