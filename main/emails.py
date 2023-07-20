from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone

from utils.email import send_email
from main.token import TokenManager
from main.permalinks import Permalink

from apps.user.models import EmailNotificationType, User


def send_password_reset(
    user: User,
    client_ip: str | None = None,
    device_type: str | None = None,
    welcome: bool = False,
) -> tuple[str, str]:
    """
    Generate a one-use only link for resetting password and send it to the
    user.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = TokenManager.password_reset_token_generator.make_token(user)
    context = {
        'welcome': welcome,
        'time': timezone.now(),
        'location': client_ip,
        'device': device_type,
        'client_reset_password': Permalink.password_reset(uid, token),
    }
    send_email(
        user,
        EmailNotificationType.PASSWORD_RESET,
        'QB: Welcome' if welcome else 'QB Password Reset',
        'emails/user/password_reset/content.html',
        'emails/user/password_reset/content.txt',
        context=context,
    )
    return uid, token


def send_password_changed_notification(user, client_ip, device_type):
    context = {
        'time': timezone.now(),
        'location': client_ip,
        'device': device_type,
        'client_forgot_password': Permalink.FORGOT_PASSWORD,
    }
    send_email(
        user,
        EmailNotificationType.PASSWORD_CHANGED,
        'QB Password Changed',
        'emails/user/password_changed/content.html',
        'emails/user/password_changed/content.txt',
        context=context,
    )
