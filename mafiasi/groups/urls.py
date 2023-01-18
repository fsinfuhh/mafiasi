from django.urls import path

from .views import *

urlpatterns = [
    path("", index, name="groups_index"),
    path("create", create, name="groups_create"),
    path("g/<slug:group_name>/", show, name="groups_show"),
    path("g/<slug:group_name>/leave", leave, name="groups_leave"),
    path("g/<slug:group_name>/invite", invite, name="groups_invite"),
    path("g/<slug:group_name>/action/<int:member_pk>", group_action, name="groups_action"),
    path("invitations/<int:invitation_pk>/action", invitation_action, name="groups_invitation_action"),
    path("invitations/<int:invitation_pk>/withdraw", withdraw_invite, name="groups_withdraw_invite"),
]
