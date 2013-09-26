from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth import get_user_model

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
        unique_together = ('jid', 'grp')

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

    def get_jid(self):
        return u'{0}@{1}'.format(self.username, settings.JABBER_DOMAIN)

class Vcard(models.Model):
    username = models.TextField(primary_key=True)
    vcard = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'vcard'

    def __unicode__(self):
        return self.username

class JabberUserMapping(models.Model):
    jabber_user = models.OneToOneField(JabberUser, on_delete=models.CASCADE)
    mafiasi_user_id = models.IntegerField(unique=True)
    class Meta:
        unique_together = ('jabber_user', 'mafiasi_user_id')
    
    def __unicode__(self):
        return u'{0} owns {1}@{2}'.format(self.mafiasi_user,
                                          self.jabber_user,
                                          settings.JABBER_DOMAIN)

    def _set_mafiasi_user(self, user):
        self.mafiasi_user_id = user.pk

    def _get_mafiasi_user(self):
        if not hasattr(self, '_mafiasi_user'):
            self._mafiasi_user = get_user_model().objects.get(pk=self.mafiasi_user_id)
        return self._mafiasi_user

    mafiasi_user = property(_get_mafiasi_user, _set_mafiasi_user)

class YeargroupSrGroupMapping(models.Model):
    yeargroup_id = models.IntegerField(unique=True)
    sr_group = models.ForeignKey(SrGroup)

    def __unicode__(self):
        return u'{0} -> {1}'.format(self.yeargroup, self.sr_group)
    
    def _get_yeargroup(self):
        if not hasattr(self, '_yeargroup'):
            self._yeargroup = Yeargroup.objects.get(pk=self.yeargroup_id)
        return self._yeargroup
    
    def _set_yeargroup(self, yeargroup):
        self.yeargroup_id = yeargroup.pk

    yeargroup = property(_get_yeargroup, _set_yeargroup)

GROUP_TYPE_CHOICES = (
    ('student', 'Student'),
    ('other', 'Other'),
)
class DefaultGroup(models.Model):
    group_type = models.CharField(max_length=16, choices=GROUP_TYPE_CHOICES)
    sr_group = models.ForeignKey(SrGroup)

    def __unicode__(self):
        return u'{0}: {1}'.format(self.get_group_type_display(), self.sr_group)

def get_account(user):
    if user.is_authenticated():
        try:
            mapping = JabberUserMapping.objects.get(mafiasi_user_id=user.pk)
            return mapping.jabber_user
        except JabberUserMapping.DoesNotExist:
            return None
    return None

def create_account(mafiasi, password):
    try:
        m = JabberUserMapping.objects.get(mafiasi_user_id=mafiasi.pk)
        return 'exists', m.jabber_user
    except JabberUserMapping.DoesNotExist:
        pass

    if mafiasi.is_student():
        group_type = 'student'
    else:
        group_type = 'other'
    
    default_groups = DefaultGroup.objects.filter(group_type=group_type) 
    sr_groups = [dg.sr_group for dg in default_groups]
    
    try:
        m = YeargroupSrGroupMapping.objects.get(yeargroup_id=mafiasi.yeargroup.pk)
        sr_groups.append(m.sr_group)
    except YeargroupSrGroupMapping.DoesNotExist:
        pass
    
    try:
        # If the user already exists, do some basic cleanup
        # This is only the case when the database is inconsistent
        user = JabberUser.objects.get(username=mafiasi.username)
        JabberUserMapping.objects.filter(jabber_user=user).delete()
        user.delete()
    except JabberUser.DoesNotExist:
        pass
    
    user = JabberUser.objects.create(username=mafiasi.username,
                                     password=password,
                                     created_at=now())
    
    JabberUserMapping.objects.create(mafiasi_user_id=mafiasi.pk, jabber_user=user)
    
    jid = user.get_jid()
    # Delete old shared roster group associations if the user had an account
    SrUser.objects.filter(jid=jid).delete()
    for sr_group in sr_groups:
        SrUser.objects.create(jid=jid, grp=sr_group.name, created_at=now())
    
    return 'created', user
