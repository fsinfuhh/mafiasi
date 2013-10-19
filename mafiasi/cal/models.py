from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

TYPE_CHOICES = (
    ('ics', _('Calendar')),
    ('vcf', _('Contact list'))
)

class DavObject(models.Model):
    username = models.CharField(max_length=120)
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    is_public = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('username', 'name', 'type')

    def __unicode__(self):
        return self.name

    def has_access(self, user, write=False):
        q = DavObject.objects.filter(user=user, object=self)
        if write:
            q = q.filter(can_write=True)
        return q.count() > 1

class DavObjectPermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    object = models.ForeignKey(DavObject)
    can_write = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'object')

    def __unicode__(self):
        mode = 'RW' if self.can_write else 'R'
        return u'{0} on {1} ({2})'.format(self.user, self.object, mode)
