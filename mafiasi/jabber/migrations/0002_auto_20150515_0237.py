# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jabber", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="privacylistdata",
            name="privacy_list",
            field=models.OneToOneField(
                related_name="data",
                primary_key=True,
                db_column="id",
                serialize=False,
                to="jabber.PrivacyList",
                on_delete=models.CASCADE,
            ),
        ),
    ]
