import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from sns_message_validator import (
    InvalidMessageTypeException,
    InvalidCertURLException,
    InvalidSignatureVersionException,
    SignatureVerificationFailureException,
    SNSMessageValidator,
)

from apps.user.models import User


logger = logging.getLogger(__name__)


sns_message_validator = SNSMessageValidator()


def verify_sns_payload(request) -> tuple[str, int]:
    # Validate message type from header without having to parse the request body.
    message_type = request.headers.get('x-amz-sns-message-type')
    try:
        sns_message_validator.validate_message_type(message_type)
        message = json.loads(request.body.decode('utf-8'))
        sns_message_validator.validate_message(message=message)
    except InvalidMessageTypeException:
        return 'Invalid message type.', 400
    except json.decoder.JSONDecodeError:
        return 'Request body is not in json format.', 400
    except InvalidCertURLException:
        return 'Invalid certificate URL.', 400
    except InvalidSignatureVersionException:
        return 'Unexpected signature version.', 400
    except SignatureVerificationFailureException:
        return 'Failed to verify signature.', 400
    return 'Success', 200


@csrf_exempt
def bounce_handler_view(request):
    if request.method != 'POST':
        # Return empty error
        return JsonResponse({'message': f'{request.method} Method not allowed'}, status=405)

    error_message, status_code = verify_sns_payload(request)
    if status_code != 200:
        logger.warning(f'Failed to handle bounce request: {error_message}')
        return JsonResponse({'message': error_message}, status=status_code)

    body = json.loads(request.body.decode('utf-8'))
    if 'SubscribeURL' in body:
        logger.warning(f'Verify subscription using this url: {body["SubscribeURL"]}')
        return JsonResponse({'message': 'Logged'}, status=200)

    # Do something with the data
    message = json.loads(body['Message'])
    notification_type = message['notificationType']
    if notification_type == 'Bounce':
        recipients = message['bounce']['bouncedRecipients']
        bounce_type = message['bounce']['bounceType']
        if bounce_type == 'Permanent':
            for recipient in recipients:
                email_address = recipient['emailAddress']
                User.objects.filter(email__iexact=email_address).update(invalid_email=True)
                logger.warning(f'Flagged {email_address} as invalid email')
    return JsonResponse({'message': 'Success'}, status=200)
