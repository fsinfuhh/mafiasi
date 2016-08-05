from django.contrib import admin

from mafiasi.base.models import Yeargroup, PasswdEntry, Mafiasi

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

class PasswdEntryAdmin(admin.ModelAdmin):
    search_fields = ['username', 'full_name']

class MafiasiChangeForm(UserChangeForm):
    class Meta:
        model = Mafiasi
        fields = '__all__'

class MafiasiAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional info', {'fields': ('account', 'yeargroup', 'real_email', 'is_guest')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional info', {'fields': ('account', 'yeargroup', 'real_email', 'is_guest')}),
    )
    form = MafiasiChangeForm

admin.site.register(Yeargroup)
admin.site.register(PasswdEntry, PasswdEntryAdmin)
admin.site.register(Mafiasi, MafiasiAdmin)
