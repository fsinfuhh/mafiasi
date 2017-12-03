# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AltCourseName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('short_name', models.CharField(max_length=30, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseToughtBy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', models.ForeignKey(related_name=b'teachers', to='teaching.Course')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('short_name', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('short_name', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('title', models.CharField(max_length=30, blank=True)),
                ('department', models.ForeignKey(related_name=b'teachers', blank=True, to='teaching.Department', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term', models.CharField(max_length=8, choices=[(b'winter', b'Winter term'), (b'summer', b'Summer term')])),
                ('year', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='department',
            name='faculty',
            field=models.ForeignKey(related_name=b'departments', blank=True, to='teaching.Faculty', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coursetoughtby',
            name='teacher',
            field=models.ForeignKey(related_name=b'courses', to='teaching.Teacher'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coursetoughtby',
            name='term',
            field=models.ForeignKey(to='teaching.Term'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='department',
            field=models.ForeignKey(related_name=b'courses', blank=True, to='teaching.Department', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='altcoursename',
            name='course',
            field=models.ForeignKey(related_name=b'alternate_names', to='teaching.Course'),
            preserve_default=True,
        ),
    ]
