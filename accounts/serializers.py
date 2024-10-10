from django.contrib.auth.hashers import check_password
from rest_framework import serializers

from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    회원가입을 위한 시리얼라이저입니다.
    """

    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ["email", "nickname", "password", "confirm_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": True},
        }


class PasswordResetSerializer(serializers.Serializer):
    """
    비밀번호 재설정을 위한 시리얼라이저입니다.
    - 현재 비밀번호와 새로운 비밀번호를 받아 비밀번호를 변경합니다.
    """

    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        """
        새로운 비밀번호의 복잡성을 검증합니다.
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                {"password": "비밀번호는 8 글자 이상이어야 합니다."}
            )
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                {"password": "1개 이상의 숫자를 포함해야 합니다. "}
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                {"password": "1개 이상의 대문자를 포함해야 합니다."}
            )
        if not any(char in r"!@#$%^&*()-_=+[{]}\|;:'\",<.>/?`~" for char in value):
            raise serializers.ValidationError(
                {"password": "1개 이상의 특수 문자를 포함해야 합니다."}
            )
        return value

    def validate(self, data):
        """
        새로운 비밀번호와 확인 비밀번호가 일치하는지 검증하고 반환합니다.
        """
        new_password = data.get("new_password")
        confirm_new_password = data.get("confirm_new_password")
        if (
            new_password
            and confirm_new_password
            and new_password != confirm_new_password
        ):
            raise serializers.ValidationError("새 비밀번호가 일치하지 않습니다.")

        user = self.context["request"].user
        if user.check_password(new_password):
            raise serializers.ValidationError(
                "이전과 동일한 비밀번호를 사용할 수 없습니다."
            )
        return data

    def validate_current_password(self, value):
        """
        현재 비밀번호가 맞는지 검증하고 그 값을 반환합니다.
        """
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("기존 비밀번호가 올바르지 않습니다.")
        return value

    def save(self, **kwargs):
        """
        비밀번호를 재설정합니다.
        - 어떠한 데이터도 직렬화하여 반환하지 않는 대신 업데이트된 사용자 객체를 반환합니다.
        """
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]

        user.set_password(new_password)
        user.save()
        return user


class StudentListSerializer(serializers.ModelSerializer):
    """
    학생 목록을 위한 시리얼라이저입니다.
    """

    class Meta:
        model = CustomUser
        fields = ["id", "email", "nickname", "created_at"]
        read_only_fields = ["id", "email", "nickname", "created_at"]


class TutorListSerializer(serializers.ModelSerializer):
    """
    강사 목록을 위한 시리얼라이저입니다.
    """

    class Meta:
        model = CustomUser
        fields = ["id", "email", "nickname", "created_at"]
        read_only_fields = ["id", "email", "nickname", "created_at"]


class CustomUserDetailSerializer(serializers.ModelSerializer):
    """
    커스텀 사용자의 시리얼라이저입니다.
    """

    confirm_password = serializers.CharField(write_only=True, required=True)

    user_type = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    tutor_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "nickname",
            "password",
            "confirm_password",
            "is_active",
            "is_staff",
            "is_superuser",
            "students",
            "user_type",
            "student_count",
            "tutor_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "is_staff",
            "is_superuser",
            "students",
            "user_type",
            "student_count",
            "tutor_count",
            "created_at",
            "updated_at",
        ]  # API로의 직접 수정 불가 필드 지정

        extra_kwargs = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": True},
        }  # 보안 강화

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

    def validate_email(self, value):
        """
        이메일 필드의 데이터를 검증합니다.
        """

        if (
            CustomUser.objects.filter(email=value)
            .exclude(id=self.instance.id if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError({"email": "사용할 수 없는 이메일입니다."})

    def validate_password(self, value):
        """
        패스워드 필드의 데이터를 검증합니다.
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                {"password": "비밀번호는 8 글자 이상이어야 합니다."}
            )
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                {"password": "1개 이상의 숫자를 포함해야 합니다. "}
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                {"password": "1개 이상의 대문자를 포함해야 합니다."}
            )
        if not any(char in r"!@#$%^&*()-_=+[{]}\|;:'\",<.>/?`~" for char in value):
            raise serializers.ValidationError(
                {"password": "1개 이상의 특수 문자를 포함해야 합니다."}
            )
        return value

    def validate_nickname(self, value):
        """
        닉네임 필드의 데이터를 검증합니다.
        """
        if (
            CustomUser.objects.filter(nickname=value)
            .exclude(id=self.instance.id if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError(
                {"nickname": "이미 존재하는 닉네임입니다."}
            )
        return value

    def validate(self, data):
        """
        전체 필드에 대한 데이터를 검증합니다.
        - 관련된 필드(password, confirm_password) 간의 데이터를 검증합니다.
        """
        data = super().validate(data)

        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        if (
            self.instance
            and password
            and check_password(password, self.instance.password)
        ):
            raise serializers.ValidationError(
                {"password": "이전과 동일한 비밀번호를 사용할 수 없습니다."}
            )
        return data

    def create(self, validated_data):
        """
        사용자 모델에 대한 시리얼라이저 객체를 생성하여 반환합니다.
        """

        try:
            password = validated_data.pop("password", None)
            validated_data.pop("confirm_password")
            user = CustomUser.objects.create_user(password=password, **validated_data)
            return user
        except Exception as e:
            raise serializers.ValidationError("사용자 생성 중 오류가 발생했습니다.")

    def update(self, instance, validated_data):
        """
        사용자 모델에 대한 시리얼라이저 객체를 수정하여 반환합니다.
        """
        try:
            password = validated_data.pop("password", None)
            validated_data.pop("confirm_password", None)

            user = super().update(instance, validated_data)

            if password:
                user.set_password(password)
                user.save()
            return user
        except Exception as e:
            raise serializers.ValidationError("사용자 업데이트 중 오류가 발생했습니다.")

    def to_representation(self, instance):
        """
        모델 인스턴스를 Python의 기본 데이터 타입(주로 딕셔너리)으로 변환합니다.
        - 보안을 위해 is_staff, date_joined 필드를 직렬화에서 제외합니다.
        - 사용자 유형에 따라 특정 필드(student_count, tutor_count, tutor)를 직렬화에서 제외합니다.
        """
        representation = super().to_representation(instance)

        representation.pop("is_staff", None)

        user_type = representation["user_type"]
        if user_type == "student":
            representation.pop("student_count", None)
            representation.pop("tutor_count", None)
        elif user_type == "tutor":
            representation.pop("tutor_count", None)
            representation.pop("tutor", None)
        else:
            representation.pop("tutor", None)

        return representation
