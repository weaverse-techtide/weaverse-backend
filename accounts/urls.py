from django.urls import path

from .views import (
    PasswordResetView,
    StudentListCreateView,
    StudentRetrieveUpdateDestroyView,
    TutorListCreateView,
    TutorRetrieveUpdateDestroyView,
    TutorStudentView,
)

app_name = "accounts"

urlpatterns = [
    path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
    path("students/", StudentListCreateView.as_view(), name="student-list-create"),
    path(
        "students/<int:pk>/",
        StudentRetrieveUpdateDestroyView.as_view(),
        name="student-detail",
    ),
    path("tutors/", TutorListCreateView.as_view(), name="tutor-list-create"),
    path(
        "tutors/<int:pk>/",
        TutorRetrieveUpdateDestroyView.as_view(),
        name="tutor-detail",
    ),
    path(
        "tutors/<int:pk>/students/",
        TutorStudentView.as_view(),
        name="tutor-student",
    ),
]
