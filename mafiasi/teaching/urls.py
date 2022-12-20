from django.urls import path

from .views import api_create_teacher, api_create_course

urlpatterns = [
    path('teacher/create', api_create_teacher, name='teaching_api_create_teacher'),
    path('course/create', api_create_course, name='teaching_api_create_course'),
]
