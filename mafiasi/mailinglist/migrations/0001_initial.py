# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Mailinglist",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("is_known", models.BooleanField(default=False)),
                ("enabled", models.BooleanField(default=True)),
                ("allow_others", models.BooleanField(default=False)),
                ("group", models.OneToOneField(to="auth.Group", on_delete=models.CASCADE)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ModeratedMail",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("email_content", models.TextField()),
                ("mailinglist", models.ForeignKey(to="mailinglist.Mailinglist", on_delete=models.CASCADE)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="RefusedRecipient",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("email", models.EmailField(max_length=75)),
                ("count", models.IntegerField(default=1)),
                ("permanent", models.BooleanField(default=False)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="WhitelistedAddress",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("email", models.EmailField(max_length=75)),
                (
                    "mailinglist",
                    models.ForeignKey(related_name="whitelist", to="mailinglist.Mailinglist", on_delete=models.CASCADE),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
