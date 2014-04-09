import re

from django.db import models
from django.utils.translation import gettext_lazy as _

TERM_CHOICES = (
    ('winter', 'Winter term'),
    ('summer', 'Summer term')
)

class Term(models.Model):
    term = models.CharField(max_length=8, choices=TERM_CHOICES)
    year = models.IntegerField()

    def __unicode__(self):
        if self.term == 'winter':
            return _('winter term {0}').format(self.year)
        elif self.term == 'summer':
            return _('summer term {0}').format(self.year)
        else:
            return unicode(self.year)

class Teacher(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    title = models.CharField(max_length=30, blank=True)

    def get_full_name(self):
        title = self.title + u' ' if self.title else u''
        return u'{0} {1} {2}'.format(title, self.first_name, self.last_name)
    
    def __unicode__(self):
        return self.get_full_name()

class Course(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name

    def get_full_name(self):
        return u'{0} ({1})'.format(self.name, self.short_name)

class AltCourseName(models.Model):
    course = models.ForeignKey(Course, related_name='alternate_names')
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.course)

class CourseToughtBy(models.Model):
    course = models.ForeignKey(Course, related_name='teachers')
    teacher = models.ForeignKey(Teacher, related_name='courses')
    term = models.ForeignKey(Term)

    def __unicode__(self):
        return u'{0}: {1} ({2})'.format(self.teacher, self.course,
                                        self.term)

def insert_autocomplete_teachers(autocomplete=None):
    if autocomplete is None:
        autocomplete = {'tokens': []}
    autocomplete['teacher'] = {}
    tokens = autocomplete['tokens']
    for teacher in Teacher.objects.all():
        autocomplete['teacher'][teacher.pk] = {
            'pk': teacher.pk,
            'full_name': teacher.get_full_name()
        }
        tokens.append({
            'token': teacher.first_name.lower(),
            'type': 'teacher',
            'pk': teacher.pk
        })
        tokens.append({
            'token': teacher.last_name.lower(),
            'type': 'teacher',
            'pk': teacher.pk
        })

def insert_autocomplete_courses(autocomplete=None):
    if autocomplete is None:
        autocomplete = {'tokens': []}
    autocomplete['course'] = {}
    tokens = autocomplete['tokens']
    for course in Course.objects.all():
        autocomplete['course'][course.pk] = {
            'pk': course.pk,
            'name': course.name,
            'short_name': course.short_name
        }
        for part in re.split(r'[\s+-]', course.name):
            tokens.append({
                'token': part.lower(),
                'type': 'course',
                'pk': course.pk

            })
        if course.short_name:
            tokens.append({
                'token': course.short_name.lower(),
                'type': 'course',
                'pk': course.pk
            })
        for alt_name in course.alternate_names.all():
            for part in re.split(r'[\s+-]', alt_name.name):
                tokens.append({
                    'token': part.lower(),
                    'type': 'course',
                    'pk': course.pk
                })
