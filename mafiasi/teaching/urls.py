from django.conf.urls import url

from .views import api_create_teacher, api_create_course

urlpatterns = [
    url(r'^teacher/create$', api_create_teacher, name='teaching_api_create_teacher'),
    url(r'^course/create$', api_create_course, name='teaching_api_create_course'),
]