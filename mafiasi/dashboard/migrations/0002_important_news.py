# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="News",
            name="important",
            field=models.BooleanField(default=False),
        ),
    ]
