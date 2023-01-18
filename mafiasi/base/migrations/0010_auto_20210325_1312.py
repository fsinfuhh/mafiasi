# Generated by Django 3.1.7 on 2021-03-25 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0009_auto_20180120_1548"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mafiasi",
            name="first_name",
            field=models.CharField(blank=True, max_length=150, verbose_name="first name"),
        ),
        migrations.AlterField(
            model_name="yeargroup",
            name="gid",
            field=models.BigIntegerField(blank=True, null=True, unique=True),
        ),
    ]
