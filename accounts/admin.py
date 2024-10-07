from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """
    강사와 관리자를 생성할 관리자 페이지입니다.
    """

    model = CustomUser
    list_display = ("email", "nickname", "is_staff", "is_superuser")
    ordering = ("email",)

    # 새 사용자 생성시 표시될 필드
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
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


admin.site.register(CustomUser, CustomUserAdmin)
