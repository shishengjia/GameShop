# Generated by Django 2.0.7 on 2018-10-15 13:51

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('price', models.IntegerField(default=100, verbose_name='price')),
                ('buy_nums', models.IntegerField(default=0, verbose_name='buy_nums')),
                ('fav_nums', models.IntegerField(default=0, verbose_name='fav_nums')),
                ('desc', models.CharField(max_length=300, verbose_name='description')),
                ('cover', models.ImageField(upload_to='course/%Y/%m', verbose_name='cover')),
                ('ram', models.IntegerField(default=4, verbose_name='ram')),
                ('cpu', models.CharField(max_length=1000, verbose_name='cpu')),
                ('hard_disk', models.IntegerField(default=8, verbose_name='hard_disk')),
                ('os', models.CharField(max_length=1000, verbose_name='os')),
                ('video_code', models.CharField(default='', max_length=1000, verbose_name='video_code')),
                ('image_1', models.ImageField(upload_to='course/%Y/%m', verbose_name='gameimage1')),
                ('image_2', models.ImageField(upload_to='course/%Y/%m', verbose_name='gameimage2')),
                ('release_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='releasetime')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='addtime')),
                ('company', models.ForeignKey(blank=True, default='1', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='company.GameCompany', verbose_name='gamecompany')),
            ],
            options={
                'verbose_name': 'GameInfo',
                'verbose_name_plural': 'GameInfo',
            },
        ),
        migrations.CreateModel(
            name='GameType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='gametype')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={
                'verbose_name': 'gametype',
                'verbose_name_plural': 'gametype',
            },
        ),
        migrations.AddField(
            model_name='game',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='game.GameType', verbose_name='gametype'),
        ),
    ]
