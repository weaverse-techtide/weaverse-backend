from django.contrib import admin
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/", include("jwtauth.urls")),
    path("api/", include("courses.urls")),
    path("api/", include("materials.urls")),
]


# api_patterns = [
#     path("accounts/", include("accounts.urls.api_urls")),
#     path("accounts/", include("allauth.urls")),
#     path("study/", include("study.urls.api_urls")),
#     path("notifications/", include("notification.urls.api_urls")),
# ]

# urlpatterns = [
#     path("api/v1/", include(api_patterns)),
# ] 
