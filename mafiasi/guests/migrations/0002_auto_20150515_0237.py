# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("guests", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invitation",
            name="email",
            field=models.EmailField(max_length=254),
        ),
    ]
