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
s
