from django.urls import path

from . import views

app_name = "materials"

urlpatterns = [
    # 이미지 관련 URL
    path("images/upload/", views.ImageCreateView.as_view(), name="image-upload"),
    path("images/", views.ImageListView.as_view(), name="image-list-create"),
    path(
        "images/<int:pk>/",
        views.ImageRetrieveUpdateDestroyView.as_view(),
        name="image-detail",
    ),
    # 동영상 관련 URL
    path("videos/upload/", views.VideoCreateView.as_view(), name="video-upload"),
    path("videos/", views.VideoListView.as_view(), name="video-list"),
    path(
        "videos/<int:pk>/",
        views.VideoRetrieveUpdateDestroyView.as_view(),
        name="video-detail",
    ),
    # 사용자 동영상 이벤트 관련 URL
    path(
        "user/<int:user_id>/video/<int:video_id>/event-occur/",
        views.UserVideoEventCreateView.as_view(),
        name="video-event-data",
    ),
    path(
        "user/<int:user_id>/video/<int:video_id>/history/",
        views.UserVideoEventListView.as_view(),
        name="video-event-list",
    ),
    path(
        "user/<int:user_id>/video/<int:video_id>/history/<int:event_id>",
        views.UserVideoEventRetrieveUpdateDestroyView.as_view(),
        name="video-event-detail",
    ),
]
