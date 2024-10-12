import jwt
from django.conf import settings
from celery import shared_task
from django.utils import timezone
from .models import BlacklistedToken

@shared_task
def delete_expired_tokens():
    now = timezone.now()
    expired_tokens = []
    for token in BlacklistedToken.objects.all():
        try:
            payload = jwt.decode(token.token, settings.SECRET_KEY, algorithms=["HS256"])
            exp = timezone.make_aware(timezone.datetime.fromtimestamp(payload['exp']))
            if exp <= now:
                expired_tokens.append(token.id)
        except jwt.ExpiredSignatureError:
            expired_tokens.append(token.id)
        except jwt.DecodeError:
            expired_tokens.append(token.id)
    
    deleted_count = BlacklistedToken.objects.filter(id__in=expired_tokens).delete()[0]
    return f"{deleted_count} expired tokens deleted."