from django.contrib import admin
from django.urls import path, include
from .views import UserInfoView, UserFavView, PayView, PayView2, OrderView, PayReturnView, PayReturnView_

app_name = 'users'
urlpatterns = [
    path('info/<int:user_id>/', UserInfoView.as_view(), name="user_info"),
    path('fav/<int:user_id>/', UserFavView.as_view(), name="user_fav"),
    path('pay/<str:info>/', PayView.as_view(), name="pay"),
    path('pay2/<int:game_id>/', PayView2.as_view(), name="pay2"),
    path('pay_return/', PayReturnView.as_view(), name="pay_return"),
    path('spay_return/', PayReturnView_.as_view(), name="spay_return"),
    path('order/', OrderView.as_view(), name="order")
]