# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mailinglist", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="moderatedmail",
            name="mailinglist",
            field=models.ForeignKey(
                related_name="moderated_mails", on_delete=models.CASCADE, to="mailinglist.Mailinglist"
            ),
        ),
        migrations.AlterField(
            model_name="refusedrecipient",
            name="email",
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name="whitelistedaddress",
            name="email",
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name="whitelistedaddress",
            name="mailinglist",
            field=models.ForeignKey(
                related_name="whitelist_addresses", on_delete=models.CASCADE, to="mailinglist.Mailinglist"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="whitelistedaddress",
            unique_together=set([("mailinglist", "email")]),
        ),
    ]
