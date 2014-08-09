from django.contrib import admin

from mafiasi.teaching.models import Faculty, Department, Teacher, Course, \
                                    AltCourseName

admin.site.register(Faculty)
admin.site.register(Department)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(AltCourseName)
