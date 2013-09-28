from django.db import models
from django.contrib.auth.models import AbstractUser

class YeargroupManager(models.Manager):
    def get_by_account(self, account):
        try:
            passwd = PasswdEntry.objects.get(username=account)
            try:
                return Yeargroup.objects.get(gid=passwd.gid)
            except Yeargroup.DoesNotExist:
                return None
        except PasswdEntry.DoesNotExist:
            return None


class Yeargroup(models.Model):
    slug = models.SlugField(max_length=16, unique=True)
    name = models.CharField(max_length=16)
    gid = models.BigIntegerField(blank=True, null=True)

    objects = YeargroupManager()

    def __unicode__(self):
        return self.name


class PasswdEntry(models.Model):
    username = models.CharField(max_length=40, unique=True)
    full_name = models.CharField(max_length=60)
    gid = models.BigIntegerField()

    def __unicode__(self):
        return self.username


class Mafiasi(AbstractUser):
    account = models.CharField(max_length=40)
    yeargroup = models.ForeignKey(Yeargroup, blank=True, null=True)
    
    def is_student(self):
        return self.account and (self.account[0].isdigit() or
                                 self.account[0] == u'x')
