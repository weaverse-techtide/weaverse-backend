from django.urls import path

from .views import (
    PasswordResetView,
    StudentListView,
    StudentRetrieveUpdateDestroyView,
    TutorListView,
    TutorRetrieveUpdateDestroyView,
    TutorStudentView,
    UserRegisterationView,
)

app_name = "accounts"

urlpatterns = [
    path("student/signup/", UserRegisterationView.as_view(), name="student-sign-up"),
    path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
    path("students/", StudentListView.as_view(), name="student-list"),
    path(
        "students/<int:pk>/",
        StudentRetrieveUpdateDestroyView.as_view(),
        name="student-detail",
    ),
    path("tutors/", TutorListView.as_view(), name="tutor-list"),
    path(
        "tutors/<int:pk>/",
        TutorRetrieveUpdateDestroyView.as_view(),
        name="tutor-detail",
    ),
    # path(
    #     "tutors/<int:pk>/students/",
    #     TutorStudentView.as_view(),
    #     name="tutor-student",
    # ),
]
