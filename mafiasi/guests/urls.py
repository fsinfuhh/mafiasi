from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.guests.views',
    url(r'^$', 'index', name='guests_index'),
    url(r'^invite$', 'invite', name='guests_invite'),
    url(r'^invited_by$', 'show_invited_by', name='guests_invited_by'),
    url(r'^accept/([a-zA-Z0-9:_-]+)$', 'accept', name='guests_accept'),
    url(r'^action$', 'invitation_action', name='guests_invitation_action'),
)
