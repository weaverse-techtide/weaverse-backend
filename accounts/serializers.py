from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    커스텀 유저의 시리얼라이저입니다.
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
            return "tutor" if obj.is_staff else "student"

        def to_representation(self, instance):
            """
            모델 인스턴스를 Python의 기본 데이터 타입(주로 딕셔너리)으로 변환합니다.
            - 유저가 student인 경우에 is_staff 필드를 특별 처리(제거)
            """
            representation = super().to_representation(instance)
            if not instance.is_staff:
                representation.pop("is_staff", None)
            return representation
