from django.contrib import admin
from django.urls import path, include
from game.views import GameListView
from django.views.static import serve
from users.views import LoginView, RegisterView, LogoutView, ForgetPassword, ResetView, ModifyPassword
from GameShop.settings import MEDIA_ROOT, MEDIA_URL
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', GameListView.as_view(), name="index"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('login/', LoginView.as_view(), name="login"),
    path('register', RegisterView.as_view(), name="register"),
    path('game', include('game.urls', namespace="game")),
    path('user', include('users.urls', namespace="user")),
    path('forget/', ForgetPassword.as_view(), name="forget_password"),
    path('reset/<str:code>/', ResetView.as_view(), name="reset password"),
    path('modify', ModifyPassword.as_view(), name="modify password"),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
