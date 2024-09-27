from django.urls import path
from .views import UserCreateView, UserDetailView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="user-register"),
    path("me/", UserDetailView.as_view(), name="user-detail"),
]
