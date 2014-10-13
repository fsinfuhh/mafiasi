from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.teaching.views',
    url(r'^teacher/create$', 'api_create_teacher', name='teaching_api_create_teacher'),
    url(r'^course/create$', 'api_create_course', name='teaching_api_create_course'),
)