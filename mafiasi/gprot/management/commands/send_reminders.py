from datetime import date
from django.core.mail import send_mail
from smtplib import SMTPException
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from raven.contrib.django.raven_compat.models import client

from mafiasi.gprot.models import Reminder


class Command(BaseCommand):
    help = 'Send emails for all reminders due today or earlier, then remove them.'

    def handle(self, *args, **options):
        reminders = Reminder.objects.select_related() \
                            .filter(exam_date__lte=date.today())

        for reminder in reminders:
            email_content = render_to_string('gprot/reminder_email.txt', {
                'course_name': reminder.course.name if reminder.course else "",
            })
            try:
                send_mail((_('Reminder: Memory minutes for "%(coursename)s"')
                            % {'coursename': reminder.course.name if reminder.course else ""}).encode('utf8'),
                          email_content.encode('utf8'),
                          None,
                          [reminder.user.email])
                reminder.delete()
            except SMTPException:
                client.captureException()
