# Generated by Django 2.0.7 on 2018-10-15 13:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GameCompany',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.TextField(verbose_name='description')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('game_nums', models.IntegerField(default=0, verbose_name='game_num')),
                ('image', models.ImageField(upload_to='company/%Y/%m', verbose_name='logo')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={
                'verbose_name': 'GameCompany',
                'verbose_name_plural': 'GameCompany',
            },
        ),
    ]
