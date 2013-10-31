import gpgme

from django.db import models
from django.conf import settings

class PGPKey(models.Model):
    fingerprint = models.CharField(max_length=40)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        unique_together = ('user', 'fingerprint')

    def __unicode__(self):
        return u'{0} ({1})'.format(self.keyid, self.user)

    def get_keyobj(self):
        ctx = gpgme.Context()
        return ctx.get_key(self.fingerprint)

class KeysigningParty(models.Model):
    name = models.CharField(max_length=60)
    event_date = models.DateField()
    submit_until = models.DateTimeField()

    def __unicode__(self):
        return self.name

class Participant(models.Model):
    party = models.ForeignKey(KeysigningParty)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    keys = models.ManyToManyField(PGPKey)

    def __unicode__(self):
        key_ids = u', '.join(key.keyid for key in self.keys.all())
        return u'{0} at {1} ({2})'.format(self.user, self.party, key_ids)
