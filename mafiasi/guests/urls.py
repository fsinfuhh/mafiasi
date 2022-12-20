from django.urls import path

from .views import index, invite, show_invited_by, accept, invitation_action

urlpatterns = [
    path('', index, name='guests_index'),
    path('invite', invite, name='guests_invite'),
    path('invited_by', show_invited_by, name='guests_invited_by'),
    path('accept/<invitation_token>', accept, name='guests_accept'),
    path('action', invitation_action, name='guests_invitation_action'),
]
