import os
from binascii import hexlify

from django.db import models
from django.conf import settings
from PyPDF2 import PdfFileReader, PdfFileWriter

from mafiasi.teaching.models import Course, Teacher

def make_filename(obj, prefix, ext):
    return '{0}/{1}-{2}.{3}'.format(
        prefix, hexlify(os.urandom(16)), obj.pk, ext)

def make_gprot_filename(gprot, filename):
    return make_filename(gprot, 'gprot', 'pdf')

def make_attachment_filename(attachment, filename):
    ext = attachment.mime_type.split('/')[-1]
    return make_filename(attachment, 'gprot-attachment', ext)

class GProt(models.Model):
    course = models.ForeignKey(Course)
    exam_date = models.DateField()
    examiners = models.ManyToManyField(Teacher)
    is_pdf = models.BooleanField(default=False)
    content = models.TextField(blank=True, null=True)
    content_pdf = models.FileField(upload_to=make_gprot_filename,
                                   null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    published = models.BooleanField(default=False)

    def __unicode__(self):
        append = ' (PDF)' if self.content_pdf else ''
        return u'[{0}] {1}: {2}{3}'.format(
            self.pk, self.exam_date, self.course, append)

    def clean_pdf_metadata(self):
        if not self.is_pdf:
            return

        title = u"GProt: {} / {}".format(
            self.course.get_full_name(),
            self.exam_date.strftime("%Y-%m-%d"),
        )
        writer = PdfFileWriter()

        # Django file fields aren't context managers :/
        self.content_pdf.open('r')
        reader = PdfFileReader(self.content_pdf)
        for i in range(reader.getNumPages()):
            writer.addPage(reader.getPage(i))
        self.content_pdf.close()

        writer.addMetadata({
            '/Title': title,
        })

        self.content_pdf.open('r+')
        writer.write(self.content_pdf)
        self.content_pdf.close()

class Attachment(models.Model):
    gprot = models.ForeignKey(GProt)
    file = models.FileField(upload_to=make_attachment_filename)
    mime_type = models.CharField(max_length=16)

    def __unicode__(self):
        return "Attachment: {0}".format(self.file.name)

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
            return self.course.get_full_name()
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
