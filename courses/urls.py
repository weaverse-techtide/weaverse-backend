from django.urls import path

from .views import (
    CourseDetailRetrieveUpdateDestroyView,
    CourseListCreateView,
    CurriculumDetailRetrieveUpdateDestroyView,
    CurriculumListCreateView,
)

app_name = "courses"
urlpatterns = [
    path("courses/", CourseListCreateView.as_view(), name="course-list"),
    path(
        "courses/<int:pk>/",
        CourseDetailRetrieveUpdateDestroyView.as_view(),
        name="course-detail",
    ),
    path(
        "curriculums/",
        CurriculumListCreateView.as_view(),
        name="curriculum-list",
    ),
    path(
        "curriculums/<int:pk>",
        CurriculumDetailRetrieveUpdateDestroyView.as_view(),
        name="curriculum-detail",
    ),
]
