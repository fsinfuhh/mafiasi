# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import mafiasi.gprot.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teaching', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=mafiasi.gprot.models.make_attachment_filename)),
                ('mime_type', models.CharField(max_length=16)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GProt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exam_date', models.DateField()),
                ('is_pdf', models.BooleanField(default=False)),
                ('content', models.TextField(null=True, blank=True)),
                ('content_pdf', models.FileField(null=True, upload_to=mafiasi.gprot.models.make_gprot_filename, blank=True)),
                ('published', models.BooleanField(default=False)),
                ('author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('course', models.ForeignKey(to='teaching.Course')),
                ('examiners', models.ManyToManyField(to='teaching.Teacher')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added_date', models.DateField()),
                ('course_query', models.CharField(max_length=100, null=True, blank=True)),
                ('course', models.ForeignKey(blank=True, to='teaching.Course', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exam_date', models.DateField()),
                ('course', models.ForeignKey(blank=True, to='teaching.Course', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='reminder',
            unique_together=set([('user', 'exam_date', 'course')]),
        ),
        migrations.AlterUniqueTogether(
            name='notification',
            unique_together=set([('user', 'course', 'course_query')]),
        ),
        migrations.AddField(
            model_name='attachment',
            name='gprot',
            field=models.ForeignKey(to='gprot.GProt'),
            preserve_default=True,
        ),
    ]
