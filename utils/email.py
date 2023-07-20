import logging

from django.utils.encoding import force_bytes
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.template import loader
from django.core.mail import EmailMultiAlternatives

from main.token import TokenManager
from apps.user.models import User, EmailNotificationType


logger = logging.getLogger(__name__)


def base_send_email(
    subject: str,
    email_html_template_name: str,
    email_text_template_name: str,
    context: dict,
    from_email: str,
    to_email: str,
):
    """
    Send a django.core.mail.EmailMultiAlternatives to `to_email`.
    Renders provided templates and send it to to_email
    Low level, Don't use this directly
    """
    # Subject
    subject = ''.join(
        # Email subject *must not* contain newlines
        subject.splitlines()
    )
    # Body
    html_content = loader.render_to_string(email_html_template_name, context)
    text_content = loader.render_to_string(email_text_template_name, context)
    # Email message
    email_message = EmailMultiAlternatives(
        subject,
        text_content,  # Plain text
        from_email,
        [to_email],
    )
    # HTML
    email_message.attach_alternative(html_content, "text/html")
    # Send email
    email_message.send()


def send_email(
    user: User,
    email_type: EmailNotificationType,
    subject: str,
    email_html_template_name: str,
    email_text_template_name: str,
    context: None | dict = None,
):
    """
    Validates email request
    Add common context variable
    """
    if user.invalid_email:
        logger.warning(
            '[{}] Email not sent: User <{}>({}) email flagged as invalid email!!'.format(
                email_type, user.email, user.pk,
            )
        )
        return
    elif not user.is_email_subscribed_for(email_type):
        logger.warning(
            '[{}] Email not sent: User <{}>({}) has not subscribed!!'.format(
                email_type, user.email, user.pk,
            )
        )
        return

    if context is None:
        context = {}
    context.update({
        'client_domain': settings.APP_FRONTEND_HOST,
        'protocol': settings.APP_HTTP_PROTOCOL,
        'site_name': settings.APP_SITE_NAME,
        'domain': settings.APP_DOMAIN,
        'user': user,
        'email_type': email_type,
        'unsubscribe_email_types': User.OPT_EMAIL_NOTIFICATION_TYPES,
        'unsubscribe_email_token':
            TokenManager.unsubscribe_email_token_generator.make_token(user),
        'unsubscribe_email_id':
            urlsafe_base64_encode(force_bytes(user.pk)),
    })

    base_send_email(
        subject,
        email_html_template_name,
        email_text_template_name,
        context,
        settings.EMAIL_FROM,
        user.email,
    )
