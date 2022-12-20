from django.urls import path

from .views import show_list, create_list, mailaction, manage_whitelist, manage_settings

urlpatterns = [
    path('<slug:group_name>', show_list, name='mailinglist_show_list'),
    path('<slug:group_name>/create', create_list,
            name='mailinglist_create_list'),
    path('<slug:group_name>/mailaction/<int:mmail_pk>', mailaction,
            name='mailinglist_mailaction'),
    path('<slug:group_name>/whitelist', manage_whitelist,
            name='mailinglist_whitelist'),
    path('<slug:group_name>/settings', manage_settings,
            name='mailinglist_settings'),
]
