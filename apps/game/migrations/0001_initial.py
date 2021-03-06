# Generated by Django 2.0.7 on 2019-02-10 23:07

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(verbose_name='comment')),
            ],
        ),
        migrations.CreateModel(
            name='Game2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('game_detail_url', models.CharField(max_length=300, verbose_name='game_detail_url')),
                ('cover_url', models.CharField(max_length=300, verbose_name='cover_detail_url')),
                ('price', models.IntegerField(default=100, verbose_name='price')),
                ('os', models.CharField(max_length=1000, verbose_name='os')),
                ('desc', models.TextField(verbose_name='description')),
                ('release_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='releasetime')),
                ('game_scree_shot_1', models.CharField(max_length=500, verbose_name='cover_detail_url')),
                ('game_scree_shot_2', models.CharField(max_length=500, verbose_name='cover_detail_url')),
                ('game_scree_shot_3', models.CharField(max_length=500, verbose_name='cover_detail_url')),
            ],
        ),
        migrations.CreateModel(
            name='GameTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='gametag')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={
                'verbose_name': 'gametag',
                'verbose_name_plural': 'gametag',
            },
        ),
        migrations.AddField(
            model_name='game2',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='game.GameTag', verbose_name='gametype'),
        ),
        migrations.AddField(
            model_name='comment',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='game.Game2', verbose_name='game2'),
        ),
    ]
