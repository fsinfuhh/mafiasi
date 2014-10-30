# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='party',
            field=models.ForeignKey(related_name=b'participants', to='pks.KeysigningParty'),
        ),
    ]
