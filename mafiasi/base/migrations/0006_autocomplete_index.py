# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20150515_0237'),
    ]

    operations = [
        migrations.RunSQL("CREATE INDEX idx_username_noyear ON base_mafiasi (regexp_replace(username, '^([0-9]+|x)', '') varchar_pattern_ops);"),
        migrations.RunSQL("CREATE INDEX idx_username ON base_mafiasi (username varchar_pattern_ops);"),
        migrations.RunSQL("CREATE INDEX idx_first_name ON base_mafiasi (lower(first_name) varchar_pattern_ops);"),
        migrations.RunSQL("CREATE INDEX idx_last_name ON base_mafiasi (lower(last_name) varchar_pattern_ops);"),
    ]
