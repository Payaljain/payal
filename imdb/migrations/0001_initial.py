# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'genre',
            },
        ),
        migrations.CreateModel(
            name='Movies',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('director', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=512)),
                ('popularity', models.DecimalField(default=0.0, max_digits=3, decimal_places=1)),
                ('score', models.DecimalField(default=0.0, max_digits=2, decimal_places=1)),
                ('genres', models.ManyToManyField(to='imdb.Genre')),
            ],
            options={
                'db_table': 'movies',
            },
        ),
    ]
