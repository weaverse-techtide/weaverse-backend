from django.urls import path

from .views import CourseDetailRetrieveUpdateDestroyView, CourseListCreateView

app_name = "courses"
urlpatterns = [
    path("courses/", CourseListCreateView.as_view(), name="course-list"),
    path(
        "courses/<int:pk>/",
        CourseDetailRetrieveUpdateDestroyView.as_view(),
        name="course-detail",
    ),
]
