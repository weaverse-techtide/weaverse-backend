from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("users/", views.user_list_create, name="user-list-create"),
    path("users/<int:pk>/", views.user_retrieve_update_delete, name="user-detail"),
    path("users/counts/", views.user_count, name="user-count"),
    path("managers/", views.manager_list_create, name="manager-list-create"),
]
