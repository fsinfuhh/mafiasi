from __future__ import unicode_literals

from smtplib import SMTPRecipientsRefused

from django.db import models
from django.utils import timezone
from django.core import signing
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from mafiasi.base.tokenbucket import TokenBucket
from mafiasi.registration.models import create_mafiasi_account

INVITATION_MAX_TOKENS = 20
INVITATION_FILL_RATE = 1.0/(3*60)

class Invitation(models.Model):
    username = models.CharField(max_length=30-len(settings.GUEST_EXTENSION), unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name='sent_invitations')
    date_invited = models.DateTimeField(default=timezone.now)
    
    def __unicode__(self):
        return self.username

    def accept_with_password(self, password):
        username = self.username + settings.GUEST_EXTENSION
        mafiasi = create_mafiasi_account(username=username,
                                         email=self.email,
                                         first_name=self.first_name,
                                         last_name=self.last_name,
                                         is_guest=True)
        mafiasi.set_password(password)
        mafiasi.save()
        Guest.objects.create(guest_user=mafiasi,
                             invited_by=self.invited_by,
                             date_invited=self.date_invited)
        self.delete()
        return mafiasi

    def send_email(self):
        token = signing.dumps(self.pk)
        site = Site.objects.get_current()
        url_path = reverse('guests_accept', args=(token,))
        activation_link = 'https://{}{}'.format(site.domain, url_path)
        email_content = render_to_string('guests/invitation_mail.txt', {
            'invitation': self,
            'activation_link': activation_link
        })
        subject = (settings.EMAIL_SUBJECT_PREFIX + 
                   'Einladung zu mafiasi.de/Invitation to mafiasi.de')
        try:
            send_mail(subject, email_content, None, [self.email])
        except SMTPRecipientsRefused:
            pass # FIXME: Inform the user
        

class Guest(models.Model):
    guest_user = models.OneToOneField(settings.AUTH_USER_MODEL)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name='invited_guests')
    date_invited = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.guest_user.username

def get_invitation_bucket(user, whatfor):
    return TokenBucket.get(identifier='invitations_sent',
                           user=user,
                           max_tokens=INVITATION_MAX_TOKENS,
                           fill_rate=INVITATION_FILL_RATE,
                           whatfor=whatfor)
