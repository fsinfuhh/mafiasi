

from email.parser import Parser, BytesParser
from email.utils import parseaddr
import logging

from mafiasi.mail import customsmtpd
from mafiasi.mailinglist.models import Mailinglist

logger = logging.getLogger('mailinglist')

class MailinglistServer(customsmtpd.RaisingSMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        if self._decode_data:
            parser = Parser()
            message = parser.parsestr(data)
        else:
            parser = BytesParser()
            message = parser.parsebytes(data)
        
        for rcptto in rcpttos:
            self.process_message_single(mailfrom, rcptto, message)

    def process_message_single(self, mailfrom, rcptto, message):
        if '@' not in rcptto:
            logger.warning('Invalid RCPTTO: {}'.format(rcptto))
            return

        try:
            mailinglist = Mailinglist.get_by_address(rcptto)
        except Mailinglist.DoesNotExist:
            logger.info('Mailinglist for address "{}" not found'.format(rcptto))
            return

        try:
            mailfrom_header = parseaddr(message['From'])[1]
        except KeyError:
            logger.info(
                    'Missing From header in email from {}'.format(mailfrom))
            return

        if mailinglist.can_send(mailfrom_header):
            mailinglist.send_email(message)
        else:
            mailinglist.moderate(message)
