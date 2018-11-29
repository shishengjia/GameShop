from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile


class GlobalSetting:
    site_title = "GameShop"


class UserProfileAdmin(UserAdmin):
    pass


admin.site.register(UserProfile, UserProfileAdmin)