# -*- encoding: utf-8 -*-

from .models import Order

from django.contrib import admin


class OrderAdmin(admin.ModelAdmin):
    list_display = ["out_trade_no", "game", 'user','order_amount', 'pay_time', "pay_status"]


admin.site.register(Order, OrderAdmin)

