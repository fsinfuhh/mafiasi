# -*- coding: utf-8 -*-


import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="News",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("title", models.CharField(max_length=120)),
                ("teaser", models.TextField()),
                ("text", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ("frontpage", models.BooleanField(default=False, db_index=True)),
                ("published", models.BooleanField(default=False)),
                ("created_by", models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                "verbose_name": "news",
                "verbose_name_plural": "news",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Panel",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("title", models.CharField(max_length=120)),
                ("content", models.TextField()),
                ("position", models.IntegerField()),
                ("shown", models.BooleanField(default=False)),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
