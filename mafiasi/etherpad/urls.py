from django.conf.urls import url

from .views import index, create_new_pad, show_pad, show_pad_html, unpin_pad, pin_pad, delete_pad

urlpatterns = [
    url(r'^$', index, name='ep_index'),
    url(r'^create_new_pad$', create_new_pad, name='ep_create_new_pad'),
    url(r'^pad/([A-Za-z0-9\-_]+)/(.+)$', show_pad, name='ep_show_pad'),
    url(r'^html/pad/([A-Za-z0-9\-_]+)/(.+)$', show_pad_html, name='ep_show_pad_html'),
    url(r'^pin/pad/([A-Za-z0-9\-_]+)/(.+)$', pin_pad, name='ep_pin_pad'),
    url(r'^unpin/pad/([A-Za-z0-9\-_]+)/(.+)$', unpin_pad, name='ep_unpin_pad'),
    url(r'^delete/([A-Za-z0-9\-_]+)/(.+)$', delete_pad, name='ep_delete_pad'),
]
