from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

<<<<<<< HEAD
# Swagger 문서화를 위한 URL 설정
urlpatterns = [
=======
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("jwtauth.urls")),
]

urlpatterns += [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
>>>>>>> fe031e56c221f89f392d7ca95166dfd2c61c253f
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
<<<<<<< HEAD
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("admin/", admin.site.urls),
    path("api/", include("jwtauth.urls")),
    path("api/", include("accounts.urls")),
=======
>>>>>>> fe031e56c221f89f392d7ca95166dfd2c61c253f
]
