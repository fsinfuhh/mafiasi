from django.urls import path

from .views import index, invitation_action, invite

urlpatterns = [
    path("", index, name="guests_index"),
    path("invite", invite, name="guests_invite"),
    path("action", invitation_action, name="guests_invitation_action"),
]
