from django.db import models
from django.conf import settings

from mafiasi.base.models import Yeargroup

class PrivacyDefaultList(models.Model):
    username = models.TextField(primary_key=True)
    name = models.TextField()
    class Meta:
        db_table = 'privacy_default_list'

    def __unicode__(self):
        return u'{0}: {1}'.format(self.username, self.name)

class PrivacyList(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.TextField()
    name = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'privacy_list'

    def __unicode__(self):
        return u'{0}: {1}'.format(self.username, self.name)

class PrivacyListData(models.Model):
    privacy_list = models.ForeignKey(PrivacyList,
        db_column='id', related_name='data')
    t = models.CharField(max_length=1)
    value = models.TextField()
    action = models.CharField(max_length=1)
    ord = models.DecimalField(max_digits=65535, decimal_places=65535)
    match_all = models.BooleanField()
    match_iq = models.BooleanField()
    match_message = models.BooleanField()
    match_presence_in = models.BooleanField()
    match_presence_out = models.BooleanField()
    class Meta:
        db_table = 'privacy_list_data'

    def __unicode__(self):
        return unicode(self.privacy_list)

class PrivateStorage(models.Model):
    username = models.TextField()
    namespace = models.TextField()
    data = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'private_storage'

    def __unicode__(self):
        return self.username

class Rostergroups(models.Model):
    username = models.TextField()
    jid = models.TextField()
    grp = models.TextField()
    class Meta:
        db_table = 'rostergroups'

    def __unicode__(self):
        return u'{0} {1}/{2}'.format(self.username, self.grp, self.jid)

class Rosteruser(models.Model):
    username = models.TextField()
    jid = models.TextField()
    nick = models.TextField()
    subscription = models.CharField(max_length=1)
    ask = models.CharField(max_length=1)
    askmessage = models.TextField()
    server = models.CharField(max_length=1)
    subscribe = models.TextField(blank=True)
    type = models.TextField(blank=True)
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'rosterusers'

    def __unicode__(self):
        return u'{0}: {1} ({2})'.format(self.username, self.nick, self.jid)

class SrGroup(models.Model):
    name = models.TextField(primary_key=True)
    opts = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'sr_group'

    def __unicode__(self):
        return self.name

class SrUser(models.Model):
    jid = models.TextField()
    grp = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'sr_user'

    def __unicode__(self):
        return u'{0} in {1}'.format(self.jid, self.grp)

class JabberUser(models.Model):
    username = models.TextField(primary_key=True)
    password = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'users'

    def __unicode__(self):
        return self.username

class Vcard(models.Model):
    username = models.TextField(primary_key=True)
    vcard = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'vcard'

    def __unicode__(self):
        return self.username

class JabberUserMapping(models.Model):
    jabber_user = models.OneToOneField(JabberUser)
    mafiasi_user = models.OneToOneField(settings.AUTH_USER_MODEL)
    class Meta:
        unique_together = ('jabber_user', 'mafiasi_user')
    
    def __unicode__(self):
        return u'{0} owns {1}@{2}'.format(self.mafiasi_user,
                                          self.jabber_user,
                                          settings.JABBER_DOMAIN) 

class YeargroupSrGroupMapping(models.Model):
    yeargroup = models.ForeignKey(Yeargroup)
    sr_group = models.OneToOneField(SrGroup)

    def __unicode__(self):
        return u'{0} -> {1}'.format(self.yeargroup, self.sr_group)
