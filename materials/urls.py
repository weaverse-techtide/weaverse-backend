from django.urls import path

from . import views

app_name = "materials"

urlpatterns = [
    # 이미지 관련 URL
    path("images/upload/", views.ImageCreateView.as_view(), name="image-upload"),
    path("images/", views.ImageListCreateView.as_view(), name="image-list-create"),
    path(
        "images/<int:pk>/",
        views.ImageRetrieveUpdateDestroyView.as_view(),
        name="image-detail",
    ),
    # 비디오 관련 URL
    path("videos/upload/", views.VideoCreateView.as_view(), name="video-upload"),
    path("videos/", views.VideoListCreateView.as_view(), name="video-list"),
    path(
        "videos/<int:pk>/",
        views.VideoRetrieveUpdateDestroyView.as_view(),
        name="video-detail",
    ),
    # 사용자 비디오 시청 기록 관련 URL
    path(
        "video-event-data/",
        views.VideoEventCreateView.as_view(),
        name="video-event-data",
    ),
    path(
        "users/<int:user_id>/videos/<int:video_id>/watch-history/",
        views.UserVideoEventListView.as_view(),
        name="video-event-list",
    ),
]
