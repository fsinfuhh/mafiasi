# Generated by Django 3.0.3 on 2020-03-05 09:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gprot", "0002_label"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gprot",
            name="labels",
            field=models.ManyToManyField(blank=True, related_name="gprots", to="gprot.Label"),
        ),
    ]
