from rest_framework import serializers
from .models import BlacklistedToken, SocialAccount
from django.contrib.auth import get_user_model


class LoginSerializer(serializers.ModelSerializer):
    """
    이 시리얼라이저는 로그인 요청을 처리합니다.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        """
        이 시리얼라이저는 User 모델을 사용합니다.
        """

        model = get_user_model()
        fields = ["email", "password"]


class SocialLoginSerializer(serializers.Serializer):
    """
    이 시리얼라이저는 소셜 로그인 요청을 처리합니다.
    """

    provider = serializers.CharField(required=True)
    access_token = serializers.CharField(required=True)

    def validate_provider(self, value):
        """
        제공자가 지원되는지 확인합니다.
        """
        supported_providers = ["google-oauth2", "kakao"]
        if value not in supported_providers:
            raise serializers.ValidationError(
                f"지원되지 않는 제공자입니다: {value}. 지원되는 제공자는 {supported_providers}입니다."
            )
        return value


class LogoutSerializer(serializers.ModelSerializer):
    """
    이 시리얼라이저는 로그아웃 요청을 처리합니다.
    """

    refresh_token = serializers.CharField()

    class Meta:
        """
        이 시리얼라이저는 BlacklistedToken 모델을 사용합니다.
        """

        model = BlacklistedToken
        fields = ["refresh_token"]


class RefreshTokenSerializer(serializers.ModelSerializer):
    """
    이 시리얼라이저는 리프레시 토큰을 검증합니다.
    """

    refresh_token = serializers.CharField()

    def validate_refresh_token(self, value):
        if BlacklistedToken.objects.filter(token=value).exists():
            raise serializers.ValidationError("유효하지 않은 리프레시 토큰입니다.")
        return value

    class Meta:
        """
        이 시리얼라이저는 BlacklistedToken 모델을 사용합니다.
        """

        model = BlacklistedToken
        fields = ["refresh_token"]


class SocialAccountSerializer(serializers.ModelSerializer):
    """
    이 시리얼라이저는 소셜 계정을 처리합니다.
    """

    class Meta:
        """
        이 시리얼라이저는 SocialAccount 모델을 사용합니다.
        """

        model = SocialAccount
        fields = ["provider", "uid"]
