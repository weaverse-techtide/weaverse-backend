from django.core.mail import send_mail
from django.conf import settings


def send_welcome_email(user):
    subject = "환영합니다! 회원가입을 축하드립니다."
    message = f"""
    안녕하세요 {user.nickname}님,

    저희 서비스에 가입해주셔서 감사합니다.
    더 나은 서비스를 제공하기 위해 항상 노력하겠습니다.

    문의사항이 있으시면 언제든 연락 주세요.

    감사합니다.
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
