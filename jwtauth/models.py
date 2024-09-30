from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blacklisted_tokens"
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
