from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    커스텀 사용자의 시리얼라이저입니다.
    """

    user_type = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    tutor_count = serializers.SerializerMethodField()

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
            "student_count",
            "tutor_count",
        ]
        read_only_fields = [
            "is_active",
            "is_staff",
            "date_joined",
            "user_type",
            "student_count",
            "tutor_count",
        ]  # API로의 직접 수정 불가 필드 지정

    def get_user_type(self, obj):
        """
        is_staff와 is_superuser 필드를 기반으로 user_type을 동적으로 제공합니다.
        """
        return (
            "student"
            if not obj.is_staff
            else ("tutor" if not obj.is_superuser else "superuser")
        )

    def get_student_count(self, obj):
        """
        학생 수를 반환합니다.
        - 관리자(superuser)나 강사(tutor)의 경우에만 제공됩니다.
        """
        if obj.is_staff or obj.is_superuser:
            return CustomUser.objects.filter(is_staff=False, is_superuser=False).count()
        return None

    def get_tutor_count(self, obj):
        """
        강사 수를 반환합니다.
        - 관리자(superuser)의 경우에만 제공됩니다.
        """
        if obj.is_superuser:
            return CustomUser.objects.filter(is_staff=True, is_superuser=False).count()
        return None

    def to_representation(self, instance):
        """
        모델 인스턴스를 Python의 기본 데이터 타입(주로 딕셔너리)으로 변환합니다.
        - 보안을 위해 is_staff, date_joined 필드를 직렬화에서 제외합니다.
        - 사용자 유형에 따라 특정 필드(student_count, tutor_count)를 직렬화에서 제외합니다.
        """
        representation = super().to_representation(instance)

        representation.pop("is_staff", None)
        representation.pop("date_joined", None)

        user_type = representation["user_type"]
        if user_type == "student":
            representation.pop("student_count", None)
            representation.pop("tutor_count", None)
        elif user_type == "tutor":
            representation.pop("tutor_count", None)
        else:
            pass  # 관리자(superuser)의 경우에는 두 필드를 제외하지 않습니다.

        representation.pop("user_type", None)

        return representation
