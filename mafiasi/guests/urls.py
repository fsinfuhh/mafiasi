from django.conf.urls import url

from .views import index, invite, show_invited_by, accept, invitation_action

urlpatterns = [
    url(r'^$', index, name='guests_index'),
    url(r'^invite$', invite, name='guests_invite'),
    url(r'^invited_by$', show_invited_by, name='guests_invited_by'),
    url(r'^accept/([a-zA-Z0-9:_-]+)$', accept, name='guests_accept'),
    url(r'^action$', invitation_action, name='guests_invitation_action'),
]
