from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("students/", views.student_list_create, name="student-list-create"),
    path(
        "students/<int:pk>/",
        views.student_retrieve_update_delete,
        name="student-detail",
    ),
    path("students/counts/", views.student_count, name="student-count"),
    path("tutors/", views.tutor_list_create, name="tutor-list-create"),
]
