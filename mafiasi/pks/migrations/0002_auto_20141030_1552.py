# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pks", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="participant",
            name="party",
            field=models.ForeignKey(related_name="participants", to="pks.KeysigningParty", on_delete=models.CASCADE),
        ),
    ]
