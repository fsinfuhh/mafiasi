import os
from binascii import hexlify

from django.db import models
from django.conf import settings

from mafiasi.teaching.models import Course, Teacher


def make_filename(obj, prefix, ext):
    return '{0}/{1}-{2}.{3}'.format(
        prefix, hexlify(os.urandom(16)), obj.pk, ext)


def make_gprot_filename(gprot, filename):
    return make_filename(gprot, 'gprot', 'pdf')


def make_attachment_filename(attachment, filename):
    ext = attachment.mime_type.split('/')[-1]
    return make_filename(attachment, 'gprot-attachment', ext)


class LabelManager(models.Manager):

    def as_choices(self):
        for label in self.order_by('name'):
            yield label.pk, label.name


class Label(models.Model):
    color_choices = [('success', 'green'),
                     ('default','grey'),
                     ('info','light blue'),
                     ('primary','blue'),
                     ('warning','yellow'),
                     ('danger','red')]
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=15, default="default", choices=color_choices)

    objects = LabelManager()

    def __str__(self):
        return self.name


class GProt(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    exam_date = models.DateField()
    examiners = models.ManyToManyField(Teacher)
    is_pdf = models.BooleanField(default=False)
    content = models.TextField(blank=True, null=True)
    content_pdf = models.FileField(upload_to=make_gprot_filename,
                                   null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    published = models.BooleanField(default=False)
    labels = models.ManyToManyField(Label, related_name='gprots', blank=True)

    def __str__(self):
        append = ' (PDF)' if self.content_pdf else ''
        return '[{0}] {1}: {2}{3}'.format(
            self.pk, self.exam_date, self.course, append)


class Attachment(models.Model):
    gprot = models.ForeignKey(GProt, on_delete=models.CASCADE)
    file = models.FileField(upload_to=make_attachment_filename)
    mime_type = models.CharField(max_length=16)

    def __str__(self):
        return "Attachment: {0}".format(self.file.name)


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    added_date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    course_query = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'course', 'course_query')

    @property
    def query_or_course_name(self):
        if self.course:
            return self.course.get_full_name()
        else:
            return self.course_query

    def __str__(self):
        return 'Notification for {0} by {1}'.format(
            self.query_or_course_name, self.user)


class Reminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam_date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'exam_date', 'course')

    def __str__(self):
        return 'Reminder for {0}, "{1}" on {2}'.format(
            self.user,
            self.course.name if self.course else "",
            self.exam_date)
