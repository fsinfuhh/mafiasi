from django.db import models
from django.conf import settings

# Create your models here.

class Ksp(models.Model):
    name = models.CharField(max_length=30)
    date = models.DateField()


class Key(models.Model):
    key_id = models.CharField(max_length=8)
    fingerprint = models.CharField(max_length=50)

class KspParticipants(models.Model):
    ksp = models.ForeignKey(Ksp)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    key = models.ForeignKey(Key)
