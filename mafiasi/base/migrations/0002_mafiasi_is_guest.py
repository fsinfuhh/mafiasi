# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="mafiasi",
            name="is_guest",
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
