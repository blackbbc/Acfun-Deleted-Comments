# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='db_ac_contents',
            fields=[
                ('cid', models.IntegerField(serialize=False, primary_key=True)),
                ('content', models.CharField(max_length=100000)),
                ('userName', models.CharField(max_length=50)),
                ('layer', models.IntegerField()),
                ('acid', models.IntegerField()),
                ('isDelete', models.IntegerField()),
                ('siji', models.IntegerField()),
                ('checkTime', models.DateTimeField(max_length=50)),
            ],
            options={
                'db_table': 'accomments',
            },
        ),
        migrations.CreateModel(
            name='db_ac_contents_delete',
            fields=[
                ('cid', models.IntegerField(serialize=False, primary_key=True)),
                ('content', models.CharField(max_length=100000)),
                ('userName', models.CharField(max_length=50)),
                ('layer', models.IntegerField()),
                ('acid', models.IntegerField()),
                ('isDelete', models.IntegerField()),
                ('siji', models.IntegerField()),
                ('checkTime', models.DateTimeField(max_length=50)),
            ],
            options={
                'db_table': 'accomments_delete',
            },
        ),
        migrations.CreateModel(
            name='db_ac_contents_info',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('userId', models.IntegerField()),
                ('type', models.CharField(max_length=10)),
                ('title', models.CharField(max_length=1000)),
                ('up', models.CharField(max_length=1000)),
                ('postTime', models.DateTimeField(max_length=50)),
                ('url', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'accommentsinfo',
            },
        ),
        migrations.CreateModel(
            name='db_ac_contents_siji',
            fields=[
                ('cid', models.IntegerField(serialize=False, primary_key=True)),
                ('content', models.CharField(max_length=100000)),
                ('userName', models.CharField(max_length=50)),
                ('layer', models.IntegerField()),
                ('acid', models.IntegerField()),
                ('isDelete', models.IntegerField()),
                ('siji', models.IntegerField()),
                ('checkTime', models.DateTimeField(max_length=50)),
            ],
            options={
                'db_table': 'accomments_siji',
            },
        ),
        migrations.CreateModel(
            name='db_ac_refresh',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('createTime', models.DateTimeField(max_length=50)),
                ('status', models.IntegerField()),
            ],
            options={
                'db_table': 'acrefresh',
            },
        ),
        migrations.CreateModel(
            name='db_comment2db',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('cid', models.IntegerField()),
                ('userName', models.CharField(max_length=50)),
                ('postDate', models.DateTimeField(max_length=50)),
                ('contents', models.CharField(max_length=10000)),
            ],
            options={
                'db_table': 'comment2db_test',
            },
        ),
        migrations.CreateModel(
            name='db_commentdb',
            fields=[
                ('cid', models.AutoField(serialize=False, primary_key=True)),
                ('userName', models.CharField(max_length=50)),
                ('postDate', models.DateTimeField(max_length=50)),
                ('sortDate', models.DateTimeField(max_length=50)),
                ('contents', models.CharField(max_length=10000)),
            ],
            options={
                'db_table': 'commentdb_test',
            },
        ),
        migrations.CreateModel(
            name='db_status',
            fields=[
                ('name', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('status', models.DateTimeField(max_length=50)),
                ('score', models.IntegerField()),
            ],
            options={
                'db_table': 'status',
            },
        ),
    ]
