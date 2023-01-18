from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import pre_delete

from mafiasi.etherpad.etherpad import Etherpad


class PinnedEtherpad(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group_name = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
    pad_name = models.CharField(max_length=30)

    def __str__(self):
        return "{}: {}".format(self.group_name, self.pad_name)


def _delete_group_ep(sender, group, **kwargs):
    ep = Etherpad()
    pads = ep.get_group_pads(group.name)
    for pad in pads:
        ep.delete_pad(pad)
    ep.delete_group(group.name)


pre_delete.connect(_delete_group_ep, sender=Group)
