from django.urls import path
from .views import LoginView, LogoutView, RefreshTokenView, SocialLoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("social-login/", SocialLoginView.as_view(), name="social_login"),
]
