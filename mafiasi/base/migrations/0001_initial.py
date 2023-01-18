# -*- coding: utf-8 -*-


import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Mafiasi",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(default=django.utils.timezone.now, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        unique=True,
                        max_length=30,
                        verbose_name="username",
                        validators=[
                            django.core.validators.RegexValidator("^[\\w.@+-]+$", "Enter a valid username.", "invalid")
                        ],
                    ),
                ),
                ("first_name", models.CharField(max_length=30, verbose_name="first name", blank=True)),
                ("last_name", models.CharField(max_length=30, verbose_name="last name", blank=True)),
                ("email", models.EmailField(max_length=75, verbose_name="email address", blank=True)),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("account", models.CharField(max_length=40)),
                (
                    "groups",
                    models.ManyToManyField(
                        related_query_name="user",
                        related_name="user_set",
                        to="auth.Group",
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of his/her group.",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        related_query_name="user",
                        related_name="user_set",
                        to="auth.Permission",
                        blank=True,
                        help_text="Specific permissions for this user.",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PasswdEntry",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("username", models.CharField(unique=True, max_length=40)),
                ("full_name", models.CharField(max_length=60)),
                ("gid", models.BigIntegerField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Yeargroup",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("slug", models.SlugField(unique=True, max_length=16)),
                ("name", models.CharField(max_length=16)),
                ("gid", models.BigIntegerField(null=True, blank=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="mafiasi",
            name="yeargroup",
            field=models.ForeignKey(blank=True, to="base.Yeargroup", on_delete=models.CASCADE, null=True),
            preserve_default=True,
        ),
    ]
