import re

from django.db import models
from django.utils.translation import gettext_lazy as _

TERM_CHOICES = (("winter", "Winter term"), ("summer", "Summer term"))


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=30)

    def __str__(self):
        return self.short_name


class DepartmentManager(models.Manager):
    def as_choices(self):
        for dep in self.all().order_by("name"):
            yield dep.pk, dep.name

    def as_grouped_choices(self):
        for dep in self.filter(faculty=None).order_by("name"):
            yield dep.pk, dep.name
        for fac in Faculty.objects.select_related().order_by("name"):
            yield fac.name, [(d.pk, d.name) for d in fac.departments.all().order_by("name")]


class Department(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="departments", blank=True, null=True)
    short_name = models.CharField(max_length=30)

    objects = DepartmentManager()

    def __str__(self):
        return self.short_name

    re.compile(r"[a-z0-9.]+@[a-z0-9.]+")


class Term(models.Model):
    term = models.CharField(max_length=8, choices=TERM_CHOICES)
    year = models.IntegerField()

    def __str__(self):
        if self.term == "winter":
            return _("winter term {0}").format(self.year)
        elif self.term == "summer":
            return _("summer term {0}").format(self.year)
        else:
            return str(self.year)


class TeacherManager(models.Manager):
    def as_choices(self):
        for teacher in self.all().order_by("last_name"):
            yield teacher.pk, str(teacher)

    def as_grouped_choices(self):
        for teacher in self.filter(department=None).order_by("last_name"):
            yield teacher.pk, str(teacher)
        for dep in Department.objects.select_related().order_by("name"):
            yield dep.name, [(t.pk, str(t)) for t in dep.teachers.all().order_by("last_name")]


class Teacher(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    title = models.CharField(max_length=30, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="teachers", blank=True, null=True)

    objects = TeacherManager()

    def get_full_name(self):
        title = self.title + " " if self.title else ""
        return "{0}{1} {2}".format(title, self.first_name, self.last_name)

    def __str__(self):
        return self.get_full_name()


class CourseManager(models.Manager):
    def as_choices(self):
        for course in self.all().order_by("name"):
            yield course.pk, str(course)

    def as_grouped_choices(self):
        for course in self.filter(department=None).order_by("name"):
            yield course.pk, str(course)
        for dep in Department.objects.select_related().order_by("name"):
            yield dep.name, [(c.pk, str(c)) for c in dep.courses.all().order_by("name")]


class Course(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=30, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="courses", blank=True, null=True)

    objects = CourseManager()

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        if self.name and self.short_name:
            return "{0} ({1})".format(self.name, self.short_name)
        elif self.short_name:
            return self.short_name
        else:
            return self.name


class AltCourseName(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="alternate_names")
    name = models.CharField(max_length=100)

    def __str__(self):
        return "{0} ({1})".format(self.name, self.course)


class CourseToughtBy(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="teachers")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="courses")
    term = models.ForeignKey(Term, on_delete=models.CASCADE)

    def __str__(self):
        return "{0}: {1} ({2})".format(self.teacher, self.course, self.term)


def insert_autocomplete_teachers(autocomplete=None):
    if autocomplete is None:
        autocomplete = {"tokens": []}
    autocomplete["teacher"] = {}
    tokens = autocomplete["tokens"]
    for teacher in Teacher.objects.all():
        autocomplete["teacher"][teacher.pk] = {"pk": teacher.pk, "full_name": teacher.get_full_name()}
        tokens.append({"token": teacher.first_name.lower(), "type": "teacher", "pk": teacher.pk})
        tokens.append({"token": teacher.last_name.lower(), "type": "teacher", "pk": teacher.pk})


def insert_autocomplete_courses(autocomplete=None):
    if autocomplete is None:
        autocomplete = {"tokens": []}
    autocomplete["course"] = {}
    tokens = autocomplete["tokens"]
    for course in Course.objects.all():
        autocomplete["course"][course.pk] = {
            "pk": course.pk,
            "name": course.name,
            "short_name": course.short_name,
            "full_name": course.get_full_name(),
        }
        for part in re.split(r"[\s+-]", course.name):
            if part:
                tokens.append({"token": part.lower(), "type": "course", "pk": course.pk})
        if course.short_name:
            tokens.append({"token": course.short_name.lower(), "type": "course", "pk": course.pk})
        for alt_name in course.alternate_names.all():
            for part in re.split(r"[\s+-]", alt_name.name):
                tokens.append({"token": part.lower(), "type": "course", "pk": course.pk})
