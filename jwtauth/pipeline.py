from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
import random

User = get_user_model()


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    """
    소셜 로그인 시 유저를 생성하거나 기존 유저와 연결하는 파이프라인 함수입니다.
    """
    if user:
        return {"is_new": False}

    email = details.get("email")
    if not email:
        return None

    social_id = backend.get_user_details(kwargs.get("response", {})).get("id")
    existing_user = User.objects.filter(email=email).first()

    social_user = UserSocialAuth.objects.filter(
        provider=backend.name, uid=social_id
    ).first()

    if social_user:
        return {"is_new": False, "user": social_user.user}
    elif existing_user:
        UserSocialAuth.objects.create(
            user=existing_user,
            provider=backend.name,
            uid=social_id,
            extra_data=kwargs.get("response", {}),
        )
        return {"is_new": False, "user": existing_user}
    else:

        nickname = details.get("nickname") or generate_meaningful_nickname()
        while User.objects.filter(nickname=nickname).exists():
            nickname = generate_meaningful_nickname()

        user = User.objects.create_user(
            email=email,
            nickname=nickname,
            password=None,
        )

        return {"is_new": True, "user": user}


def generate_meaningful_nickname():
    """
    뜻있는 닉네임을 생성해주는 함수입니다.
    """
    adjectives = [
        "귀여운",
        "멋진",
        "훌륭한",
        "빛나는",
        "멋있는",
        "뜨거운",
        "차가운",
        "새로운",
        "신선한",
        "행복한",
        "즐거운",
        "강한",
        "용감한",
        "현명한",
        "착한",
        "친절한",
        "재미있는",
        "열정적인",
        "능력있는",
        "창의적인",
    ]
    nouns = [
        "고래",
        "사자",
        "호랑이",
        "코끼리",
        "기린",
        "팬더",
        "토끼",
        "거북이",
        "독수리",
        "펭귄",
        "여우",
        "늑대",
        "곰",
        "돌고래",
        "캥거루",
        "코알라",
        "참새",
        "부엉이",
        "앵무새",
        "고양이",
    ]

    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    number = random.randint(1, 999)

    return f"{adjective}{noun}{number:03d}"
