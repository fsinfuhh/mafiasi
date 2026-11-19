from datetime import date
from smtplib import SMTPException

import sentry_sdk
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from mafiasi.gprot.models import Reminder


class Command(BaseCommand):
    help = "Send emails for all reminders due today or earlier, then remove them."

    def handle(self, *args, **options):
        reminders = Reminder.objects.select_related().filter(exam_date__lte=date.today())

        for reminder in reminders:
            email_content = render_to_string(
                "gprot/reminder_email.txt",
                {
                    "course_name": reminder.course.name if reminder.course else "",
                },
            )
            try:
                send_mail(
                    (
                        _('Reminder: Memory minutes for "%(coursename)s"')
                        % {"coursename": reminder.course.name if reminder.course else ""}
                    ).encode("utf8"),
                    email_content.encode("utf8"),
                    None,
                    [reminder.user.email],
                )
                reminder.delete()
            except SMTPException:
                sentry_sdk.capture_exception()
