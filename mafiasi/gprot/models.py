from django.db import models
from django.conf import settings
import hashlib

from mafiasi.teaching.models import Course, Teacher

def make_filename(gprot, filename):
    return 'gprot/{0}.{1}.pdf'.format(
        hashlib.md5(unicode(gprot).encode('utf8')).hexdigest(), gprot.pk)

class GProt(models.Model):
    course = models.ForeignKey(Course)
    exam_date = models.DateField()
    examiners = models.ManyToManyField(Teacher)
    is_pdf = models.BooleanField(default=False)
    content = models.TextField(blank=True, null=True)
    content_pdf = models.FileField(upload_to=make_filename, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    published = models.BooleanField(default=False)

    def __unicode__(self):
        append = ' (PDF)' if self.content_pdf else ''
        return u'[{0}] {1}: {2}{3}'.format(
            self.pk, self.exam_date, self.course, append)

class Attachment(models.Model):
    gprot = models.ForeignKey(GProt)
    file = models.FileField(upload_to=make_attachment_filename)

    def __unicode__(self):
        return "Attachment [{0}] of {1}".format(self.gprot.pk, self.file_.url)

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    added_date = models.DateField()
    course = models.ForeignKey(Course, blank=True, null=True)
    course_query = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'course', 'course_query')

    @property
    def query_or_course_name(self):
        if self.course:
            return self.course.name
        else:
            return self.course_query

    def __unicode__(self):
        return u'Notification for {0} by {1}'.format(
            self.query_or_course_name, self.user)

class Reminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    exam_date = models.DateField()
    course = models.ForeignKey(Course, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'exam_date', 'course')

    def __unicode__(self):
        return u'Reminder for {0}, "{1}" on {2}'.format(
            self.user, self.course.name, self.exam_date)
