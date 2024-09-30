from django.urls import path

from .views import CourseListCreateView

app_name = "courses"
urlpatterns = [
    path("courses/", CourseListCreateView.as_view(), name="course-list"),
]
