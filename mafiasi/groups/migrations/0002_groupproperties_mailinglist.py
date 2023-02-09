# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("groups", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="groupproperties",
            name="has_mailinglist",
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
