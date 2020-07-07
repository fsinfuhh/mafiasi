from html import escape

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from mafiasi.base.models import Yeargroup, Mafiasi

import logging

class PrivacyDefaultList(models.Model):
    username = models.TextField(primary_key=True)
    name = models.TextField()
    class Meta:
        db_table = 'privacy_default_list'

    def __str__(self):
        return '{0}: {1}'.format(self.username, self.name)

class PrivacyList(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.TextField()
    name = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'privacy_list'

    def __str__(self):
        return '{0}: {1}'.format(self.username, self.name)

class PrivacyListData(models.Model):
    privacy_list = models.OneToOneField(PrivacyList, on_delete=models.CASCADE,
        db_column='id', related_name='data', primary_key=True)
    t = models.CharField(max_length=1)
    value = models.TextField()
    action = models.CharField(max_length=1)
    ord = models.IntegerField()
    match_all = models.BooleanField(default=False)
    match_iq = models.BooleanField(default=False)
    match_message = models.BooleanField(default=False)
    match_presence_in = models.BooleanField(default=False)
    match_presence_out = models.BooleanField(default=False)
    class Meta:
        db_table = 'privacy_list_data'

    def __str__(self):
        return str(self.privacy_list)

class PrivateStorage(models.Model):
    username = models.TextField()
    namespace = models.TextField()
    data = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'private_storage'

    def __str__(self):
        return self.username

class Rostergroups(models.Model):
    username = models.TextField()
    jid = models.TextField()
    grp = models.TextField()
    class Meta:
        db_table = 'rostergroups'

    def __str__(self):
        return '{0} {1}/{2}'.format(self.username, self.grp, self.jid)

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

    def __str__(self):
        return '{0}: {1} ({2})'.format(self.username, self.nick, self.jid)

class SrGroup(models.Model):
    name = models.TextField(primary_key=True)
    opts = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'sr_group'

    def __str__(self):
        return self.name

class SrUser(models.Model):
    jid = models.TextField()
    grp = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'sr_user'
        unique_together = ('jid', 'grp')

    def __str__(self):
        return '{0} in {1}'.format(self.jid, self.grp)

class JabberUser(models.Model):
    username = models.TextField(primary_key=True)
    password = models.TextField(default='NO_PASSWORDS_IN_DB_ZYYJN53N3M5QMHNQKLOAQD7E')
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

    def get_jid(self):
        return '{0}@{1}'.format(self.username, settings.JABBER_DOMAIN)

    def set_nickname(self, nickname):
        Vcard.objects.filter(username=self.username).delete()
        vcard_tpl = "<vCard xmlns='vcard-temp'><NICKNAME>{nick}</NICKNAME></vCard>"
        vcard_xml = vcard_tpl.format(nick=escape(nickname, quote=True))
        try:
            vcard = Vcard.objects.get(username=self.username)
            vcard.vcard = vcard_xml
        except Vcard.DoesNotExist:
            vcard = Vcard(username=self.username,
                          vcard=vcard_xml,
                          created_at=now())
        vcard.save()

class Vcard(models.Model):
    username = models.TextField(primary_key=True)
    vcard = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        db_table = 'vcard'

    def __str__(self):
        return self.username

class JabberUserMapping(models.Model):
    jabber_user = models.OneToOneField(JabberUser, on_delete=models.CASCADE)
    mafiasi_user_id = models.IntegerField(unique=True)
    class Meta:
        unique_together = ('jabber_user', 'mafiasi_user_id')
    
    def __str__(self):
        return '{0} owns {1}@{2}'.format(self.mafiasi_user,
                                          self.jabber_user,
                                          settings.JABBER_DOMAIN)

    def _set_mafiasi_user(self, user):
        self.mafiasi_user_id = user.pk

    def _get_mafiasi_user(self):
        if not hasattr(self, '_mafiasi_user'):
            User = get_user_model()
            try:
                self._mafiasi_user = User.objects.get(pk=self.mafiasi_user_id)
            except User.DoesNotExist:
                self._mafiasi_user = None
        return self._mafiasi_user

    mafiasi_user = property(_get_mafiasi_user, _set_mafiasi_user)

class YeargroupSrGroupMapping(models.Model):
    yeargroup_id = models.IntegerField(unique=True)
    sr_group = models.ForeignKey(SrGroup, on_delete=models.CASCADE)

    def __str__(self):
        return '{0} -> {1}'.format(self.yeargroup, self.sr_group)
    
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
    sr_group = models.ForeignKey(SrGroup, on_delete=models.CASCADE)

    def __str__(self):
        return '{0}: {1}'.format(self.get_group_type_display(), self.sr_group)

def get_or_create_account(user):
    try:
        mapping = JabberUserMapping.objects.get(mafiasi_user_id=user.pk)
        return mapping.jabber_user
    except JabberUserMapping.DoesNotExist:
        return create_jabber_account(user)

@receiver(post_save, sender=Mafiasi)
def _account_creation_cb(instance, created, **kwargs):
    if created:
        create_jabber_account(instance)

def create_jabber_account(mafiasi):
    if mafiasi.is_student:
        group_type = 'student'
    else:
        group_type = 'other'
    
    default_groups = DefaultGroup.objects.filter(group_type=group_type) 
    sr_groups = [dg.sr_group for dg in default_groups]
    
    if mafiasi.yeargroup:
        try:
            m = YeargroupSrGroupMapping.objects.get(
                    yeargroup_id=mafiasi.yeargroup.pk)
            sr_groups.append(m.sr_group)
        except YeargroupSrGroupMapping.DoesNotExist:
            logging.exception("Jabber yeargroup missing for user %s", mafiasi)
    
    user = JabberUser.objects.create(username=mafiasi.username,
                                     created_at=now())
    
    if mafiasi.first_name:
        nickname = '{0} ({1})'.format(mafiasi.first_name, mafiasi.username)
    else:
        nickname = mafiasi.username
    user.set_nickname(nickname)
    
    JabberUserMapping.objects.create(mafiasi_user_id=mafiasi.pk, jabber_user=user)
    
    jid = user.get_jid()
    for sr_group in sr_groups:
        SrUser.objects.create(jid=jid, grp=sr_group.name, created_at=now())

    return user
