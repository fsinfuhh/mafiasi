import copy
import logging
import smtplib
import socket
from email.parser import BytesParser, Parser
from email.utils import formataddr, getaddresses

from django.conf import settings

from mafiasi.base.models import Mafiasi

from . import customsmtpd

logger = logging.getLogger("mailcloak")


class CloakServer(customsmtpd.RaisingSMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        if self._decode_data:
            parser = Parser()
            message = parser.parsestr(data)
        else:
            parser = BytesParser()
            message = parser.parsebytes(data)

        rcptto_addresses = [addr[1].lower() for addr in getaddresses(rcpttos)]
        cloaks = self.get_cloaks(rcptto_addresses)

        for rcptto_address in rcptto_addresses:
            if rcptto_address in cloaks:
                rcptmessage = self.uncloak_message(message, rcptto_address, cloaks)
                rcptto = cloaks[rcptto_address]
            else:
                rcptto = rcptto_address
                rcptmessage = message
            self.process_message_single(mailfrom, rcptto, rcptmessage)

    def process_message_single(self, mailfrom, rcptto, message):
        refused = {}
        try:
            s = smtplib.SMTP()
            s.connect(settings.EMAIL_HOST, settings.EMAIL_PORT)
            refused = s.sendmail(mailfrom, [rcptto], message.as_string())
        except smtplib.SMTPRecipientsRefused as e:
            refused = e.recipients
        except (socket.error, smtplib.SMTPException) as e:
            logger.exception(e)
            return

        for recipient_email, smtp_error in list(refused.items()):
            logger.info("Recipient {} refused ({}: {})".format(recipient_email, smtp_error[0], smtp_error[1]))

    def get_cloaks(self, addresses):
        cloaks = {}
        cloak_users = []
        for address in addresses:
            local_part, domain = address.split("@", 1)
            if domain == settings.MAILCLOAK_DOMAIN:
                cloak_users.append(local_part)
        for cloak_user in Mafiasi.objects.filter(username__in=cloak_users):
            cloak_email = "{}@{}".format(cloak_user.username, settings.MAILCLOAK_DOMAIN)
            cloaks[cloak_email] = cloak_user.real_email
        return cloaks

    def uncloak_message(self, message, rcptto, cloaks):
        message = copy.deepcopy(message)
        for field in ("To", "Cc"):
            self._uncloak_field(message, rcptto, cloaks, field)
        return message

    def _uncloak_field(self, message, rcptto, cloaks, field):
        addresses = getaddresses(message.get_all(field, []))
        del message[field]
        for name, address in addresses:
            address_lower = address.lower()
            if rcptto == address_lower:
                address = cloaks.get(address_lower, address)
            message.add_header(field, formataddr((name, address)))
