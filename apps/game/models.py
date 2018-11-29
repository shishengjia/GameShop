# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models

from company.models import GameCompany


class GameType(models.Model):
    name = models.CharField(max_length=20, verbose_name="gametype")
    add_time = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = "gametype"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Game(models.Model):
    company = models.ForeignKey(GameCompany, verbose_name="gamecompany", null=True, blank=True, default="1", on_delete=models.DO_NOTHING)
    type = models.ForeignKey(GameType, verbose_name="gametype", null=True, blank=True, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=50, verbose_name=u"name")
    price = models.IntegerField(default=100, verbose_name="price")
    buy_nums = models.IntegerField(default=0, verbose_name="buy_nums")
    fav_nums = models.IntegerField(default=0, verbose_name="fav_nums")
    desc = models.CharField(max_length=300, verbose_name=u"description")
    cover = models.ImageField(upload_to="game/%Y/%m", verbose_name="cover")
    ram = models.IntegerField(default=4, verbose_name="ram")
    cpu = models.CharField(max_length=1000, verbose_name="cpu")
    hard_disk = models.IntegerField(default=8, verbose_name="hard_disk")
    os = models.CharField(max_length=1000, verbose_name="os")
    video_code = models.CharField(max_length=1000, default="", verbose_name="video_code")
    image_1 = models.ImageField(upload_to="game/%Y/%m", verbose_name="gameimage1")
    image_2 = models.ImageField(upload_to="game/%Y/%m", verbose_name="gameimage2")
    release_time = models.DateTimeField(default=datetime.now, verbose_name="releasetime")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="addtime")

    class Meta:
        verbose_name = "GameInfo"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name