from django.contrib import admin

from mafiasi.teaching.models import Faculty, Department, Teacher, Course, \
                                    AltCourseName

class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name')
    ordering = ('name',)
admin.site.register(Faculty, FacultyAdmin)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'faculty')
    ordering = ('faculty', 'short_name')
admin.site.register(Department, DepartmentAdmin)

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'department')
    ordering = ('department', 'last_name')
    search_fields = ('first_name', 'last_name')
admin.site.register(Teacher, TeacherAdmin)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'department')
    ordering = ('department', 'name')
    search_fields = ('name', 'short_name')
admin.site.register(Course, CourseAdmin)
admin.site.register(AltCourseName)
