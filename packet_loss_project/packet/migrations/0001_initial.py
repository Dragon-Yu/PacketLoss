# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-11-14 03:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('only_creator_can_see', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Packet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('content', models.TextField()),
                ('latitude', models.DecimalField(decimal_places=12, max_digits=16)),
                ('longitude', models.DecimalField(decimal_places=12, max_digits=16)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('likes', models.IntegerField(default=0)),
                ('dislikes', models.IntegerField(default=0)),
                ('can_see_time', models.DateTimeField()),
                ('die_time', models.DateTimeField()),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_packets', to=settings.AUTH_USER_MODEL)),
                ('ignorers', models.ManyToManyField(related_name='ignored_packets', to=settings.AUTH_USER_MODEL)),
                ('last_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('owneders', models.ManyToManyField(related_name='owned_packets', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owning_packets', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='packet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='packet.Packet'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
