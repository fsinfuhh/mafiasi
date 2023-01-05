from django.urls import path

from .views import index, show_news

urlpatterns = [
    path('', index, name='dashboard_index'),
    path('news/<int:news_pk>', show_news, name='dashboard_show_news'),
]
