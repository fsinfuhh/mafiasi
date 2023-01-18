# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import migrations, models

import mafiasi.pks.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AssignedKey",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("fingerprint", models.CharField(max_length=40)),
                ("user", models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={},
            bases=(models.Model, mafiasi.pks.models.KeyMixin),
        ),
        migrations.CreateModel(
            name="KeysigningParty",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("name", models.CharField(max_length=60)),
                ("event_date", models.DateField()),
                ("submit_until", models.DateTimeField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Participant",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("keys", models.ManyToManyField(to="pks.AssignedKey")),
                ("party", models.ForeignKey(to="pks.KeysigningParty", on_delete=models.CASCADE)),
                ("user", models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PGPKey",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("fingerprint", models.CharField(max_length=40)),
            ],
            options={},
            bases=(models.Model, mafiasi.pks.models.KeyMixin),
        ),
        migrations.AlterUniqueTogether(
            name="assignedkey",
            unique_together=set([("user", "fingerprint")]),
        ),
    ]
