from django.db import models
from django.conf import settings
from accounts.models import CustomUser


class BlacklistedToken(models.Model):
    """
    client가 로그아웃을 요청하거나 토큰이 만료되었을 때 토큰을 블랙리스트에 추가합니다.
    class Meta에 인덱스를 추가하여 검색을 빠르게 합니다.
    """

    token = models.CharField(max_length=500, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blacklisted_tokens",
    )
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    token_type = models.CharField(
        max_length=10, choices=[("access", "Access"), ("refresh", "Refresh")]
    )

    def __str__(self):
        return f"{self.token_type.capitalize()} token {self.token[:20]}... blacklisted at {self.blacklisted_at}"

    class Meta:
        """
        블랙리스트 토큰을 검색하기 쉽게 인덱스를 추가합니다.
        """

        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user", "token_type"]),
        ]


class SocialAccount(models.Model):
    """
    소셜 로그인을 위한 사용자의 소셜 계정 uid와 제공자를 저장합니다.
    """

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="social_accounts"
    )
    uid = models.CharField(max_length=255)
    provider = models.CharField(max_length=50)

    class Meta:
        """
        소셜 계정을 통합하여 중복을 방지합니다.
        """

        unique_together = ("provider", "uid")
