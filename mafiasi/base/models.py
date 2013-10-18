import os
import base64
import hashlib

from ldapdb.models.fields import CharField as ldapCharField, \
                                 IntegerField as ldapIntegerField, \
                                 ListField as ldapListField
import ldapdb.models

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.utils.crypto import constant_time_compare
from django.contrib.auth.models import AbstractUser, Group

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
    new_password = None
    
    def is_student(self):
        return self.account and (self.account[0].isdigit() or
                                 self.account[0] == u'x')

    def set_password(self, new_password):
        """ Set attribute new_password after changing a password.

        This way other parts of this app can register to Mafiasi.post_save
        signal and access the plaintext password for changing it in their
        service.
        """
        super(Mafiasi, self).set_password(new_password)
        self.new_password = new_password


class LdapGroup(ldapdb.models.Model):
    base_dn = 'ou=groups,' + settings.ROOT_DN
    object_classes = ['posixGroup']

    gid = ldapIntegerField(db_column='gidNumber', unique=True)
    name = ldapCharField(db_column='cn', primary_key=True)
    members = ldapListField(db_column='memberUid')

    def __unicode__(self):
        return self.name


class LdapUser(ldapdb.models.Model):
    base_dn = 'ou=People,' + settings.ROOT_DN
    object_classes = ['person', 'inetOrgPerson']

    id = ldapIntegerField(db_column='employeeNumber', unique=True)
    username = ldapCharField(db_column='uid', primary_key=True)
    display_name = ldapCharField(db_column='cn')
    first_name = ldapCharField(db_column='givenName')
    last_name = ldapCharField(db_column='sn')
    email = ldapCharField(db_column='mail')
    password = ldapCharField(db_column='userPassword')

    def __unicode__(self):
        return self.username
    
    def set_password(self, password):
        salt = os.urandom(8)
        digest = hashlib.sha256(password.encode('utf-8') + salt).digest()
        self.password = '{SSHA256}' + base64.b64encode(digest + salt)

    def check_password(self, password):
        if not self.password.startswith('{SSHA256}'):
            raise ValueError('Only SSHA256 is supported')
        base64_data = self.password[len('{SSHA256}'):]
        expected_digest = base64_data[:32]
        salt = base64_data[32:]
        given_digest = hashlib.sha256(password + salt).digest()
        return constant_time_compare(given_digest, expected_digest)


def _change_user_cb(sender, instance, created, **kwargs):
    try:
        ldap_user = LdapUser.objects.get(pk=instance.username)
    except LdapUser.DoesNotExist:
        ldap_user = LdapUser(username=instance.username)

    ldap_user.id = instance.id
    ldap_user.display_name = instance.username
    ldap_user.first_name = instance.first_name
    ldap_user.last_name = instance.last_name
    ldap_user.email = instance.email

    if instance.new_password:
        ldap_user.set_password(instance.new_password)
    ldap_user.save()

post_save.connect(_change_user_cb, sender=Mafiasi)

def _change_group_cb(sender, instance, created, **kwargs):
    try:
        ldap_group = LdapGroup.objects.get(pk=instance.name)
    except LdapGroup.DoesNotExist:
        ldap_group = LdapGroup(name=instance.name)
    ldap_group.gid = instance.id
    ldap_group.save()
post_save.connect(_change_group_cb, sender=Group)
