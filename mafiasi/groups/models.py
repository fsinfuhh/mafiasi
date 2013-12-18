import re

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from mafiasi.base.models import LdapGroup, LOCK_ID_LDAP_GROUP
from mafiasi.base.utils import AdvisoryLock

class GroupError(Exception):
    pass

class GroupProperties(models.Model):
    group = models.OneToOneField(Group, related_name='properties')
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL,
            related_name='admin_of')
    public_members = models.BooleanField(default=False)
    
    def get_ldap_group(self):
        return LdapGroup.objects.get(gid=self.group.pk)

    def __unicode__(self):
        return unicode(self.group)

class GroupProxy(object):
    def __init__(self, group):
        self.group = group

    def add_member(self, user):
        group = self.group
        with AdvisoryLock(LOCK_ID_LDAP_GROUP, group.pk):
            ldap_group = LdapGroup.objects.get(gid=group.pk)
            ldap_group.members.append(user.username)
            ldap_group.save()
            group.user_set.add(user)

    def remove_member(self, user, check_admin=False):
        with AdvisoryLock(LOCK_ID_LDAP_GROUP, self.group.pk):
            properties = self.group.properties
            if check_admin:
                self._raise_if_sole_admin(user)
            properties.admins.remove(user)
            ldap_group = LdapGroup.objects.get(gid=self.group.pk)
            try:
                ldap_group.members.remove(user.username)
                ldap_group.save()
            except ValueError:
                pass
            self.group.user_set.remove(user)
    
    def grant_admin(self, user):
        self.group.properties.admins.add(user)

    def revoke_admin(self, user):
        self._raise_if_sole_admin(user)
        self.group.properties.admins.remove(user)

    def _raise_if_sole_admin(self, user):
        properties = self.group.properties
        if properties.admins.filter(pk=user.pk):
            num_admins = properties.admins.count()
            if num_admins == 1:
                msg = _('You are the sole group admin. Please terminate the '
                        'group or appoint another group admin.')
                raise GroupError(msg)

class GroupInvitation(models.Model):
    date_invited = models.DateTimeField(default=now)
    group = models.ForeignKey(Group, related_name='invitations')
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL,
            related_name='invitations')
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
            related_name='given_invitations')

    def __unicode__(self):
        return u'Invitation to {0} for {1}'.format(self.group, self.invitee)

    def accept(self):
        group_proxy = GroupProxy(self.group)
        group_proxy.add_member(self.invitee)
        self.delete()

    def refuse(self):
        self.delete()

_group_name_re = re.compile(r'^[a-zA-Z]([a-zA-Z0-9_-]*)$')
def create_usergroup(user, name):
    if not _group_name_re.match(name):
        raise GroupError(_('Invalid group name.'))
    
    if Group.objects.filter(name__iexact=name).count():
        raise GroupError(_('Group does already exist.'))
    
    group = Group.objects.create(name=name)

    group_proxy = GroupProxy(group)
    group_proxy.add_member(user)

    group.properties.admins.add(user)

    return group

def _change_group_cb(sender, instance, created, **kwargs):
    if created:
        props = GroupProperties.objects.create(group=instance)
        instance.properties = props
post_save.connect(_change_group_cb, sender=Group)
