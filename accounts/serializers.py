from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    커스텀유저의 시리얼라이저입니다.
    """

    user_type = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "user_type",
        ]
        read_only_fields = [
            "is_active",
            "is_staff",
            "user_type",
        ]  # API로의 직접 수정 불가 필드 지정

        def get_user_type(self, obj):
            """
            is_staff 필드를 기반으로 user_type을 동적으로 제공합니다.
            """
            return "manager" if obj.is_staff else "student"
