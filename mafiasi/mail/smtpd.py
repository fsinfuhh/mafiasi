from __future__ import absolute_import

import smtpd

from raven.contrib.django.raven_compat.models import client

class SMTPServer(smtpd.SMTPServer):
    def handle_error(self):
        client.captureException()
