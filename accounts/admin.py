from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    관리자로 하여금 커스텀 사용자 모델을 관리하기 위해 제공되는 관리자 클래스입니다.
    - 모델로 CustomUser를 사용합니다.
    - 커스텀 사용자 수정 및 생성 폼을 제공합니다.
    - 커스텀 사용자 목록을 조회할 수 있으며, 필터링 및 검색 옵션을 제공합니다.
    - 커스텀 사용자 목록에 표시될 필드들과 정렬 기준을 제공합니다.
    - 모든 유형의 커스텀 사용자을 생성하는 기능을 제공합니다.
    """

    model = CustomUser

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Login info", {"fields": ("email", "nickname", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "introduction")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "Important dates",
            {
                "fields": ("last_login", "created_at", "updated_at"),
                "classes": ("wide",),
            },
        ),
    )

    add_fieldsets = (
        (
            "Register info",
            {
                "fields": (
                    "email",
                    "nickname",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    list_display = ("email", "nickname", "is_staff", "is_superuser")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "nickname", "first_name", "last_name")
    ordering = ("email", "created_at")

    def save_model(self, request, obj, form, change):
        if not change:
            if form.cleaned_data.get("is_staff") and not form.cleaned_data.get(
                "is_superuser"
            ):
                CustomUser.objects.create_staff(
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password1"],
                    nickname=form.cleaned_data["nickname"],
                )
            elif form.cleaned_data.get("is_superuser"):
                CustomUser.objects.create_superuser(
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password1"],
                    nickname=form.cleaned_data["nickname"],
                )
            else:
                CustomUser.objects.create_user(
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password1"],
                    nickname=form.cleaned_data["nickname"],
                )
        else:
            obj.email = form.cleaned_data.get("email", obj.email)
            obj.nickname = form.cleaned_data.get("nickname", obj.nickname)
            if "password1" in form.cleaned_data:
                obj.set_password(form.cleaned_data["password1"])
            obj.is_staff = form.cleaned_data.get("is_staff", obj.is_staff)
            obj.is_superuser = form.cleaned_data.get("is_superuser", obj.is_superuser)
            obj.save()
