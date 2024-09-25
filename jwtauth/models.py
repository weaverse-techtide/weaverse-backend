from django.db import models


class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blacklisted token {self.token[:20]}... at {self.blacklisted_at}"


# Todo Refresh Token Rotation - 재사용 토큰을 블랙리스트에 추가, 사용를 제한
# 블랙리스트 캐시를 어디로 옮길지 결정해야함... 장고 내장? 레디스?
# class TokenRotation(models.Model):
