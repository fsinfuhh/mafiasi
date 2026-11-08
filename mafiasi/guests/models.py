from smtplib import SMTPRecipientsRefused

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mafiasi.base.tokenbucket import TokenBucket

INVITATION_MAX_TOKENS = 20
INVITATION_FILL_RATE = 1.0 / (3 * 60)


def build_invite_link(pk: str) -> str:
    base = settings.OPENID_ISSUER.split("/application/")[0]
    return f"{base}/if/flow/guest-enrollment/?itoken={pk}"


class Invitation(models.Model):
    authentik_pk = models.UUIDField(null=True, blank=True, unique=True)
    username = models.CharField(max_length=30)
    email = models.EmailField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    invited_by = models.CharField(max_length=30)
    date_invited = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username

    def send_email(self, request):
        activation_link = build_invite_link(str(self.authentik_pk))
        email_content = render_to_string(
            "guests/invitation_mail.txt", {"invitation": self, "activation_link": activation_link}
        )
        subject_de = "Einladung zu " + settings.PROJECT_NAME + " / " if settings.MAIL_INCLUDE_GERMAN else ""
        subject = settings.EMAIL_SUBJECT_PREFIX + subject_de + "Invitation to " + settings.PROJECT_NAME
        try:
            send_mail(subject, email_content, None, [self.email])
        except (SMTPRecipientsRefused, ConnectionRefusedError):
            messages.error(
                request,
                _("Sending the invitation email failed, please try again later"),
            )


def get_invitation_bucket(user, whatfor):
    return TokenBucket.get(
        identifier="invitations_sent",
        user=user,
        max_tokens=INVITATION_MAX_TOKENS,
        fill_rate=INVITATION_FILL_RATE,
        whatfor=whatfor,
    )
