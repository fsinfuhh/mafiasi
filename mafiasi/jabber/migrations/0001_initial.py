# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_type', models.CharField(max_length=16, choices=[(b'student', b'Student'), (b'other', b'Other')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JabberUser',
            fields=[
                ('username', models.TextField(serialize=False, primary_key=True)),
                ('password', models.TextField()),
                ('created_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JabberUserMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mafiasi_user_id', models.IntegerField(unique=True)),
                ('jabber_user', models.OneToOneField(to='jabber.JabberUser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrivacyDefaultList',
            fields=[
                ('username', models.TextField(serialize=False, primary_key=True)),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'privacy_default_list',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrivacyList',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('username', models.TextField()),
                ('name', models.TextField()),
                ('created_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'privacy_list',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrivacyListData',
            fields=[
                ('privacy_list', models.ForeignKey(related_name=b'data', primary_key=True, db_column=b'id', serialize=False, to='jabber.PrivacyList')),
                ('t', models.CharField(max_length=1)),
                ('value', models.TextField()),
                ('action', models.CharField(max_length=1)),
                ('ord', models.IntegerField()),
                ('match_all', models.BooleanField(default=False)),
                ('match_iq', models.BooleanField(default=False)),
                ('match_message', models.BooleanField(default=False)),
                ('match_presence_in', models.BooleanField(default=False)),
                ('match_presence_out', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'privacy_list_data',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrivateStorage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.TextField()),
                ('namespace', models.TextField()),
                ('data', models.TextField()),
                ('created_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'private_storage',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rostergroups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.TextField()),
                ('jid', models.TextField()),
                ('grp', models.TextField()),
            ],
            options={
                'db_table': 'rostergroups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rosteruser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.TextField()),
                ('jid', models.TextField()),
                ('nick', models.TextField()),
                ('subscription', models.CharField(max_length=1)),
                ('ask', models.CharField(max_length=1)),
                ('askmessage', models.TextField()),
                ('server', models.CharField(max_length=1)),
                ('subscribe', models.TextField(blank=True)),
                ('type', models.TextField(blank=True)),
                ('created_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'rosterusers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SrGroup',
            fields=[
                ('name', models.TextField(serialize=False, primary_key=True)),
                ('opts', models.TextField()),
                ('created_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sr_group',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SrUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jid', models.TextField()),
                ('grp', models.TextField()),
                ('created_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sr_user',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vcard',
            fields=[
                ('username', models.TextField(serialize=False, primary_key=True)),
                ('vcard', models.TextField()),
                ('created_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'vcard',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='YeargroupSrGroupMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yeargroup_id', models.IntegerField(unique=True)),
                ('sr_group', models.ForeignKey(to='jabber.SrGroup')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='sruser',
            unique_together=set([('jid', 'grp')]),
        ),
        migrations.AlterUniqueTogether(
            name='jabberusermapping',
            unique_together=set([('jabber_user', 'mafiasi_user_id')]),
        ),
        migrations.AddField(
            model_name='defaultgroup',
            name='sr_group',
            field=models.ForeignKey(to='jabber.SrGroup'),
            preserve_default=True,
        ),
    ]
