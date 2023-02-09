# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0003_merge"),
    ]

    operations = [
        migrations.AddField(
            model_name="mafiasi",
            name="real_email",
            field=models.EmailField(max_length=75, unique=True, null=True),
            preserve_default=True,
        ),
    ]
