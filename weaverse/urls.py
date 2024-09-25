from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Swagger 문서화를 위한 설정
schema_view = get_schema_view(
    openapi.Info(
        title="Weaverse API",
        default_version="v1",
        description="Weaverse 교육 플랫폼 API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
        license=openapi.License(name="Apache License 2.0"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Swagger 문서화를 위한 URL 설정
urlpatterns = [
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("admin/", admin.site.urls),
    path("api/", include("jwtauth.urls")),
    path("api/", include("accounts.urls")),
]
