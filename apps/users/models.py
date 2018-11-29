# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    mobile = models.CharField(max_length=11, null=True, blank=True)
    image = models.ImageField(upload_to="image/%Y/%m", default=u"image/default.png", max_length=100)

    class Meta:
        verbose_name = "UserInfo"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class EmailVerifyCode(models.Model):
    code = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)

    send_time = models.DateTimeField(default=datetime.now)

