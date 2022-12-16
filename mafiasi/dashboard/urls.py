from django.conf.urls import re_path, path

from .views import index, show_news

urlpatterns = [
    path('', index, name='dashboard_index'),
    re_path(r'^news/(\d+)$', show_news, name='dashboard_show_news'),
]
