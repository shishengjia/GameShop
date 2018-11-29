from django.contrib import admin
from django.urls import path, include
from game.views import GameDetailView, AddFavoriteView

app_name = 'game'
urlpatterns = [
    path('detail/<int:game_id>/', GameDetailView.as_view(), name="detail"),
    path('add_fav/', AddFavoriteView.as_view(), name="add_fav"),
]
