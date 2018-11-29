# -*- encoding: utf-8 -*-

from .models import GameCompany

from django.contrib import admin


class GameCompanyAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(GameCompany, GameCompanyAdmin)

