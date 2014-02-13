from django.db import models
from django.conf import settings

from mafiasi.teaching.models import Course, Teacher

class GProt(models.Model):
    course = models.ForeignKey(Course)
    exam_date = models.DateField()
    examiner = models.ForeignKey(Teacher)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    def __unicode__(self):
        return u'[{0}] {1}: {2}'.format(self.pk, self.exam_date, self.course)

class Attachment(models.Model):
    gprot = models.ForeignKey(GProt)
    filename = models.CharField(max_length=80)

class Reminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    exam_date = models.DateField()

    def __unicode__(self):
        return u'Reminder for {0} on {1}'.format(self.user, self.exam_date)
