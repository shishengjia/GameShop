# -*- encoding: utf-8 -*-
from datetime import datetime

from django.db import models


class GameCompany(models.Model):
    desc = models.TextField(verbose_name="description")
    name = models.CharField(max_length=50, verbose_name="name")
    game_nums = models.IntegerField(default=0, verbose_name="game_num")
    image = models.ImageField(upload_to="company/%Y/%m", verbose_name="logo")
    add_time = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = "GameCompany"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_game_nums(self):
        return self.game_set.all().count()
    get_game_nums.short_description = "game_num"

