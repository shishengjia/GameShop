# -*- encoding: utf-8 -*-

from .models import Game, GameType

from django.contrib import admin


class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', "type"]

class GameTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Game, GameAdmin)
admin.site.register(GameType, GameTypeAdmin)

