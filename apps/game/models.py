# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models

from company.models import GameCompany


class GameTag(models.Model):
    name = models.CharField(max_length=20, verbose_name="gametag")
    add_time = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = "gametag"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_game_num(self):
        return self.game2_set.count()


class Game2(models.Model):
    name = models.CharField(max_length=200, verbose_name="name")
    game_detail_url = models.CharField(max_length=300, verbose_name="game_detail_url")
    cover_url = models.CharField(max_length=300, verbose_name="cover_detail_url")
    price = models.IntegerField(default=100, verbose_name="price")
    tag = models.ForeignKey(GameTag, verbose_name="gametype", null=True, blank=True, on_delete=models.DO_NOTHING)
    os = models.CharField(max_length=1000, verbose_name="os")
    desc = models.TextField(verbose_name="description")
    release_time = models.DateTimeField(default=datetime.now, verbose_name="releasetime")
    game_scree_shot_1 = models.CharField(max_length=500, verbose_name="cover_detail_url")
    game_scree_shot_2 = models.CharField(max_length=500, verbose_name="cover_detail_url")
    game_scree_shot_3 = models.CharField(max_length=500, verbose_name="cover_detail_url")


class Comment(models.Model):
    game = models.ForeignKey(Game2, verbose_name="game2", null=True, blank=True, on_delete=models.DO_NOTHING)
    comment = models.TextField(verbose_name="comment")



