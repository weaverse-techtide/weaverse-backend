from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("users/", views.student_list_create, name="user-list-create"),
    path("users/<int:pk>/", views.student_retrieve_update_delete, name="user-detail"),
    path("users/counts/", views.student_count, name="user-count"),
    path("managers/", views.tutor_list_create, name="manager-list-create"),
]
