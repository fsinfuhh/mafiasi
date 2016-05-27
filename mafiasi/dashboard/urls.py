from django.conf.urls import url

from .views import index, show_news

urlpatterns = [
    url(r'^$', index, name='dashboard_index'),
    url(r'^news/(\d+)$', show_news, name='dashboard_show_news'),
]
