from django.template.response import TemplateResponse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from main.token import TokenManager
from apps.user.models import User


# XXX: Needs testing
def unsubscribe_email(
    request,
    uidb64: str,
    token: str,
    email_type: str,
) -> TemplateResponse:
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist,
    ):
        user = None

    context = {
        'success': True,
        'title': 'Unsubscribe Email',
    }

    token_generator = TokenManager.unsubscribe_email_token_generator
    if user is not None and token_generator.check_token(user, token):
        user.unsubscribe_email(email_type, save=True)
    else:
        context['success'] = False

    return TemplateResponse(
        request,
        'web/admin/user/unsubscribe_email__confirm.html',
        context
    )
