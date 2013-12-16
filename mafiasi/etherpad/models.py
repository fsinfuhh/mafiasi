from django.db.models.signals import pre_delete
from django.contrib.auth.models import Group


from mafiasi.etherpad.etherpad import Etherpad

def _delete_group_ep(sender, group, using):
    ep = Etherpad()
    pads = ep.get_group_pads(group.name)
    for pad in pads:
        ep.delete_pad(pad)
    ep.delete_grop(group.name)
pre_delete.connect(_delete_group_ep, sender=Group)
