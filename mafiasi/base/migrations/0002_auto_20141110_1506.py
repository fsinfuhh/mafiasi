# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TokenBucket",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("identifier", models.CharField(max_length=30)),
                ("max_tokens", models.IntegerField()),
                ("fill_rate", models.FloatField()),
                ("tokens", models.FloatField(default=0.0)),
                ("last_updated", models.DateTimeField()),
                ("user", models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="tokenbucket",
            unique_together=set([("identifier", "user")]),
        ),
    ]
