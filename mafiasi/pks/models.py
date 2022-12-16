from datetime import datetime
import gpgme
from zoneinfo import ZoneInfo

from django.db import models
from django.conf import settings


class KeyMixin(object):
    def get_keyobj(self):
        ctx = gpgme.Context()
        return ctx.get_key(self.fingerprint)


class PGPKey(models.Model, KeyMixin):
    fingerprint = models.CharField(max_length=40)
    
    def __str__(self):
        return self.fingerprint


class AssignedKey(models.Model, KeyMixin):
    fingerprint = models.CharField(max_length=40)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'fingerprint')

    def __str__(self):
        return '{0} ({1})'.format(self.fingerprint, self.user)


class KeysigningParty(models.Model):
    name = models.CharField(max_length=60)
    event_date = models.DateField()
    submit_until = models.DateTimeField()

    def submission_expired(self):
        return datetime.now(ZoneInfo("UTC")) > self.submit_until

    def __str__(self):
        return self.name


class Participant(models.Model):
    party = models.ForeignKey(KeysigningParty, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    keys = models.ManyToManyField(AssignedKey)

    def __str__(self):
        key_ids = ', '.join(key.fingerprint for key in self.keys.all())
        return '{0} at {1} ({2})'.format(self.user, self.party, key_ids)
