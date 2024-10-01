from django.db import models
from django.conf import settings


class BlacklistedToken(models.Model):
    """
    해당 모델은 블랙리스트에 추가된 토큰을 저장합니다.
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
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user", "token_type"]),
        ]
