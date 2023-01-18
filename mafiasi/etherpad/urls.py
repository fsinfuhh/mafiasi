from django.urls import path

from .views import (
    create_new_pad,
    delete_pad,
    index,
    pin_pad,
    show_pad,
    show_pad_html,
    unpin_pad,
)

urlpatterns = [
    path("", index, name="ep_index"),
    path("create_new_pad", create_new_pad, name="ep_create_new_pad"),
    path("pad/<slug:group_name>/<path:pad_name>", show_pad, name="ep_show_pad"),
    path("html/pad/<slug:group_name>/<path:pad_name>", show_pad_html, name="ep_show_pad_html"),
    path("pin/pad/<slug:group_name>/<path:pad_name>", pin_pad, name="ep_pin_pad"),
    path("unpin/pad/<slug:group_name>/<path:pad_name>", unpin_pad, name="ep_unpin_pad"),
    path("delete/<slug:group_name>/<path:pad_name>", delete_pad, name="ep_delete_pad"),
]
