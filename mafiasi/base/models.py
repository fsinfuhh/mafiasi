import os
import base64
import hashlib

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from django.dispatch import receiver
from django.utils.crypto import constant_time_compare
from django.contrib.auth.models import AbstractUser, Group

from mafiasi.base.tokenbucket import TokenBucket # noqa
from mafiasi.utils.ldapmodel import LdapModel, LdapAttr, LdapNotFound
from mafiasi.base.validation import validate_ascii

LOCK_ID_LDAP_GROUP = -215652734


class YeargroupManager(models.Manager):
    def get_by_domain(self, domain):
        domain = settings.REGISTER_DOMAIN_MAPPING[domain]
        yeargroup, _created = Yeargroup.objects.get_or_create(slug=domain, defaults={'name': domain})
        return yeargroup


class Yeargroup(models.Model):
    slug = models.SlugField(max_length=16, unique=True)
    name = models.CharField(max_length=16)
    gid = models.BigIntegerField(blank=True, null=True, unique=True)

    objects = YeargroupManager()

    def __str__(self):
        return self.name


@receiver(pre_save, sender=Yeargroup)
def yeargroup_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        # when instance.id is None, the object was just created
        try:
            # Sometimes, gids are reused. In this case, unset the old group's gid first.
            same_gid_group = Yeargroup.objects.get(gid=instance.gid)
            same_gid_group.gid = None
            same_gid_group.save()
        except Yeargroup.DoesNotExist:
            # No problem, no conflicting group
            pass


class Mafiasi(AbstractUser):
    account = models.CharField(max_length=64, validators=[validate_ascii])
    yeargroup = models.ForeignKey(Yeargroup, on_delete=models.CASCADE, blank=True, null=True)
    is_guest = models.BooleanField(default=False)
    real_email = models.EmailField(unique=True, null=True)
    new_password = None

    # USED in contrib.auth to determine the mail address for thinks like password reset
    EMAIL_FIELD = 'real_email'

    @property
    def is_student(self):
        return self.account and (self.account[0].isdigit() or
                                 self.account[0] == 'x')

    def set_password(self, new_password):
        """ Set attribute new_password after changing a password.

        This way other parts of this app can register to Mafiasi.post_save
        signal and access the plaintext password for changing it in their
        service.
        """
        super(Mafiasi, self).set_password(new_password)
        self.new_password = new_password

    def get_ldapuser(self):
        return LdapUser.lookup(self.username)


class LdapGroup(LdapModel):
    base_dn = 'ou=groups,' + settings.ROOT_DN
    lookup_dn = 'cn={},' + base_dn
    primary_key = 'name'
    object_classes = [b'posixGroup']
    attrs = {
        'gid': LdapAttr('gidNumber'),
        'name': LdapAttr('cn'),
        'members': LdapAttr('memberUid', multi=True)
    }

    def __str__(self):
        return self.name


class LdapUser(LdapModel):
    base_dn = 'ou=People,' + settings.ROOT_DN
    lookup_dn = 'uid={},' + base_dn
    primary_key = 'username'
    object_classes = [b'person', b'inetOrgPerson', b'ownCloud']
    attrs = {
        'id': LdapAttr('employeeNumber'),
        'username': LdapAttr('uid'),
        'common_name': LdapAttr('cn'),
        'display_name': LdapAttr('displayName'),
        'first_name': LdapAttr('givenName'),
        'last_name': LdapAttr('sn'),
        'email': LdapAttr('mail'),
        'password': LdapAttr('userPassword'),
        'nextcloud_quota': LdapAttr('ownCloudQuota')
    }

    def __str__(self):
        return self.username
    
    def set_password(self, password):
        salt = os.urandom(8)
        digest = hashlib.sha1(password.encode('utf-8') + salt).digest()
        self.password = (b'{SSHA}' + base64.b64encode(digest + salt)).decode()

    def check_password(self, password):
        if not self.password.startswith('{SSHA}'):
            raise ValueError('Only SSHA is supported')
        password_data = base64.b64decode(self.password[len('{SSHA}'):])
        expected_digest = password_data[:20]
        salt = password_data[20:]
        given_digest = hashlib.sha1(password + salt).digest()
        return constant_time_compare(given_digest, expected_digest)


def _change_user_cb(sender, instance, created, **kwargs):
    try:
        ldap_user = LdapUser.lookup(instance.username)
    except LdapNotFound:
        ldap_user = LdapUser()
        ldap_user.username = instance.username

    ldap_user.id = str(instance.id)
    ldap_user.common_name = instance.username
    
    if created:
        if instance.first_name:
            display_name = '{} ({})'.format(instance.first_name,
                                            instance.username)
        else:
            display_name = instance.username
        ldap_user.display_name = display_name

    if instance.first_name:
        ldap_user.first_name = instance.first_name
    if instance.last_name:
        ldap_user.last_name = instance.last_name
    else:
        ldap_user.last_name = 'Unknown'
    if instance.email:
        ldap_user.email = instance.email

    if instance.new_password:
        ldap_user.set_password(instance.new_password)
    ldap_user.save()

post_save.connect(_change_user_cb, sender=Mafiasi)

def _change_group_cb(sender, instance, created, **kwargs):
    try:
        ldap_group = LdapGroup.lookup(instance.name)
    except LdapNotFound:
        ldap_group = LdapGroup()
        ldap_group.name = instance.name

    ldap_group.gid = str(instance.id)
    ldap_group.save()
post_save.connect(_change_group_cb, sender=Group)
