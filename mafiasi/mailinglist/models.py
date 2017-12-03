

from base64 import b64encode, b64decode
from email.parser import Parser
from email.utils import parseaddr
import logging
import smtplib
import socket

from django.db import models
from django.contrib.auth.models import Group
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string

from mafiasi.mail.signals import collect_mailaddresses, mailaddresses_known

logger = logging.getLogger('mailinglist')

class Mailinglist(models.Model):
    group = models.OneToOneField(Group)
    is_known = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    allow_others = models.BooleanField(default=False)

    def __unicode__(self):
        return self.get_address()
    
    def get_address(self):
        return '{}@{}'.format(self.group.name.lower(),
                              settings.MAILINGLIST_DOMAIN)

    def get_bounce_address(self):
        return '{}@bounce.{}'.format(self.group.name.lower(),
                                     settings.MAILINGLIST_DOMAIN)

    def can_send(self, email_address):
        email_address = email_address.lower()
        if self.allow_others:
            return True
        if self.group.user_set.filter(real_email=email_address).count():
            return True
        if self.whitelist_addresses.filter(email=email_address).count():
            return True
        return False

    def moderate(self, email_obj):
        if 'From' not in email_obj:
            return None
        email_data = email_obj.as_string()
        email_content = b64encode(email_data)
        modmail = ModeratedMail.objects.create(mailinglist=self,
                                               email_content=email_content)
        modmail._parsed_message = email_obj
        
        # Send information about moderation to group admins
        connection = mail.get_connection()
        for admin in self.group.properties.admins.all():
            message = self._build_moderation_mail(
                    'admin', [admin.email], modmail, email_data, admin)
            message.connection = connection
            message.send(fail_silently=True)

        # Inform the sender about moderation
        message = self._build_moderation_mail(
                'sender', [email_obj['From']], modmail, email_data, None)
        message.connection = connection
        message.send(fail_silently=True)

        return modmail

    def send_email(self, email_obj):
        excluded_emails = self._get_excluded_emails(email_obj)
        self._prepare_email_obj(email_obj)

        refused = {}
        try:
            s = smtplib.SMTP()
            s.connect(settings.EMAIL_HOST, settings.EMAIL_PORT)
            try:
                mailfrom = self.get_bounce_address()
                rcpttos = [user.email for user in self.group.user_set.all()
                           if user.email not in excluded_emails]
                refused = s.sendmail(mailfrom, rcpttos, email_obj.as_string())
            finally:
                s.quit()
        except smtplib.SMTPRecipientsRefused as e:
            refused = e.recipients
        except (socket.error, smtplib.SMTPException) as e:
            logger.exception(e)
            return
        for recipient_email, smtp_error in list(refused.items()):
            permanent = 500 <= smtp_error[0] < 600
            refused_rcpt, _created = RefusedRecipient.objects.get_or_create(
                    email=recipient_email)
            refused_rcpt.count += 1
            refused_rcpt.permanent = refused_rcpt.is_permanent() or permanent
            refused_rcpt.save()

    def _prepare_email_obj(self, email_obj):
        del_headers = ('Sender', 'List-Id', 'List-Post', 'Return-Path',
                       'Precedence', 'Errors-To', 'X-BeenThere',
                       'X-Original-To')
        for header in del_headers:
            del email_obj[header]
        list_addr = self.get_address()
        email_obj['Sender'] = list_addr
        email_obj['List-Id'] = list_addr
        email_obj['List-Post'] = '<mailto:{}>'.format(list_addr)
        email_obj['Precedence'] = 'list'
        email_obj['Errors-To'] = self.get_bounce_address()
        email_obj['X-BeenThere'] = list_addr
        subject = email_obj.get('Subject', '')
        del email_obj['Subject']
        prefix_lower = '[{}]'.format(self.group.name).lower()
        add_prefix = prefix_lower not in subject.lower()
        if add_prefix:
            email_obj['Subject'] = '[{}] {}'.format(self.group.name, subject)
        else:
            email_obj['Subject'] = subject

    def _get_excluded_emails(self, email_obj):
        excluded_emails = set()
        excluded_emails.update(email_obj.get_all('To', []))
        excluded_emails.update(email_obj.get_all('Cc', []))
        refused_rcpt = RefusedRecipient.objects.filter(permanent=True)
        excluded_emails.update(rcpt.email for rcpt in refused_rcpt)
        return {parseaddr(x.lower())[1] for x in excluded_emails}

    def _build_moderation_mail(self, template, recipient, modmail, email_data, user):
        subject = {
            'admin': ('Email an {list} wartet auf Moderation/'
                      'Email is awaiting moderation'),
            'sender': ('Deine Email an {list} wartet auf Genehmigung/'
                       'Your email is awaiting approval')
        }.get(template).format(list=self.get_address())
        template_file = 'mailinglist/moderated_mail_{}.mail'.format(template)
        body = render_to_string(template_file, {
            'mailinglist': self,
            'moderated_mail': modmail,
            'user': user
        })
        message = mail.EmailMessage(
                subject=subject,
                body=body,
                from_email=self.get_bounce_address(),
                to=recipient)
        message.attach('moderated.eml', email_data, 'message/rfc822')
        return message

    @classmethod
    def get_by_address(cls, email_address):
        local_part, domain = email_address.lower().split('@', 1)
        return cls.objects.get(group__name__iexact=local_part)

class WhitelistedAddress(models.Model):
    mailinglist = models.ForeignKey(Mailinglist,
                                    related_name='whitelist_addresses')
    email = models.EmailField()

    def __unicode__(self):
        return '[{}] {}'.format(self.mailinglist.group.name, self.email)

    class Meta:
        unique_together = ('mailinglist', 'email')

class ModeratedMail(models.Model):
    mailinglist = models.ForeignKey(Mailinglist, related_name='moderated_mails')
    email_content = models.TextField()

    def __unicode__(self):
        return '[{}] {}'.format(self.mailinglist.group.name, self.subject)
    
    def get_email(self):
        if not hasattr(self, '_parsed_message'):
            parser = Parser()
            email_content = b64decode(self.email_content)
            self._parsed_message = parser.parsestr(email_content)
        return self._parsed_message

    @property
    def subject(self):
        email_obj = self.get_email()
        try:
            return email_obj['Subject'].decode('utf-8', 'replace')
        except KeyError:
            return ''

    @property
    def sender(self):
        email_obj = self.get_email()
        try:
            return email_obj['From'].decode('utf-8', 'replace')
        except KeyError:
            return ''
    
    def unmoderate(self):
        self.mailinglist.send_email(self.get_email())
        self.delete()

class RefusedRecipient(models.Model):
    email = models.EmailField()
    count = models.IntegerField(default=1)
    permanent = models.BooleanField(default=False)

    def __unicode__(self):
        return self.email

    def is_permanent(self):
        return self.permanent or self.count > 2

def _attach_group_addresses(sender, addresses, **kwargs):
    for mailinglist in Mailinglist.objects.select_related('group'):
        addresses.append(mailinglist.get_address())

def _attach_known_addresses(sender, **kwargs):
    Mailinglist.objects.filter(is_known=False).update(is_known=True)

collect_mailaddresses.connect(_attach_group_addresses)
mailaddresses_known.connect(_attach_known_addresses)
