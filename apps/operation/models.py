# -*- encoding: utf-8 -*-
from datetime import datetime
from django.db import models

from users.models import UserProfile
from game.models import Game2


class UserFavorite(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name="user", on_delete=models.DO_NOTHING)
    fav_game_id = models.IntegerField(default=0, verbose_name="fav_game_id")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="addtime")

    class Meta:
        verbose_name = "userfav"
        verbose_name_plural = verbose_name


class UserGame(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name="user", on_delete=models.DO_NOTHING)
    game = models.ForeignKey(Game2, verbose_name="game", on_delete=models.DO_NOTHING)
    add_time = models.DateTimeField(default=datetime.now, verbose_name="add_time")

    class Meta:
        verbose_name = "usergame"
        verbose_name_plural = verbose_name


class Order(models.Model):

    user = models.ForeignKey(UserProfile, verbose_name="user", on_delete=models.DO_NOTHING)
    game = models.ForeignKey(Game2, verbose_name="game", on_delete=models.DO_NOTHING)
    out_trade_no = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="merchant trade_no")
    trade_no = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="alipay trade_no")
    pay_status = models.CharField(default="wait_for_pay", max_length=30, verbose_name="pay_status")
    order_amount = models.FloatField(default=0.0, verbose_name="order_amount")
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="pay_time")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="add_time")

    class Meta:
        verbose_name = "order"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.out_trade_no)
