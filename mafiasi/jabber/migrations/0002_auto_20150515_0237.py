# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jabber', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privacylistdata',
            name='privacy_list',
            field=models.OneToOneField(related_name='data', primary_key=True, db_column=b'id', serialize=False, to='jabber.PrivacyList'),
        ),
    ]
