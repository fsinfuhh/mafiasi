from django.db import models
from django.conf import settings

# Create your models here.
"""
class Ksp(models.Model):
    name = models.CharField(max_length=30)
    date = models.DateField()

    def __unicode__(self):
        return str(self.name) + ' ' + str(self.date)


class Key(models.Model):
    key_id = models.CharField(max_length=8)
    fingerprint = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.key_id)

class KspParticipants(models.Model):
    ksp = models.ForeignKey(Ksp)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    key = models.ForeignKey(Key)

    def __unicode__(self):
        return str(self.key.key_id) + ' nimmt an ' + str(self.ksp.name) + ' teil (' + str(self.user) + ')'
"""
