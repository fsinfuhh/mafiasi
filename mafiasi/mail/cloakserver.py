from __future__ import unicode_literals

from email.parser import Parser
from email.utils import getaddresses
import logging
import smtpd
import smtplib
import socket

from django.conf import settings

from mafiasi.base.models import Mafiasi

logger = logging.getLogger('mailcloak')

class CloakServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data):
        parser = Parser()
        message = parser.parsestr(data)
        
        rcptto_addresses = [addr[1].lower() for addr in getaddresses(rcpttos)]
        cloaks = self.get_cloaks(rcptto_addresses)

        for rcptto_addresses in rcptto_addresses:
            rcptto = cloaks.get(rcptto_addresses, rcptto_addresses)
            self.process_message_single(mailfrom, rcptto, message)

    def process_message_single(self, mailfrom, rcptto, message):
        refused = {}
        try:
            s = smtplib.SMTP()
            s.connect(settings.EMAIL_HOST, settings.EMAIL_PORT)
            refused = s.sendmail(mailfrom, [rcptto], message.as_string())
        except smtplib.SMTPRecipientRefused as e:
            refused = e.recipients
        except (socket.error, smtplib.SMTPException) as e:
            logger.exception(e)
            return

        for recipient_email, smtp_error in refused.items():
            logger.info('Recipient {} refused ({}: {})'.format(
                    recipient_email, smtp_error[0], smtp_error[1]))

    def get_cloaks(self, addresses):
        cloaks = {}
        cloak_users = []
        for address in addresses:
            local_part, domain = address.split('@', 1)
            if domain == settings.MAILCLOAK_DOMAIN:
                cloak_users.append(local_part)
        for cloak_user in Mafiasi.objects.filter(username__in=cloak_users):
            cloak_email = '{}@{}'.format(cloak_user.username,
                                         settings.MAILCLOAK_DOMAIN)
            cloaks[cloak_email] = cloak_user.email
        return cloaks
