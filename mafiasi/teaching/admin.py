from django.contrib import admin

from mafiasi.teaching.models import Teacher, Course, AltCourseName

admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(AltCourseName)
