from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="vault_index"),
]
