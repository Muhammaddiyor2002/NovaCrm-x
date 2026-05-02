from __future__ import annotations

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import ChangePasswordView, LoginView, MeView, RegisterView

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("password/change/", ChangePasswordView.as_view(), name="password-change"),
]
