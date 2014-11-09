from django.contrib import admin

from mafiasi.guests.models import Invitation, Guest

class InvitationAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'invited_by', 'date_invited')

class GuestAdmin(admin.ModelAdmin):
    list_display = ('guest_user', 'invited_by', 'date_invited')

admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Guest, GuestAdmin)
