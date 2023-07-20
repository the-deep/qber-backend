import requests
from rest_framework import serializers
from django.conf import settings


HCAPTCHA_VERIFY_URL = 'https://hcaptcha.com/siteverify'


def validate_hcaptcha(captcha):
    if not captcha:
        return False
    data = {
        'secret': settings.HCAPTCHA_SECRET,
        'response': captcha,
    }
    response = requests.post(url=HCAPTCHA_VERIFY_URL, data=data)
    response_json = response.json()
    return response_json['success']


class CaptchaSerializerMixin(serializers.Serializer):
    captcha = serializers.CharField(write_only=True, required=True)

    def validate_captcha(self, captcha):
        if not validate_hcaptcha(captcha):
            raise serializers.ValidationError('Invalid captcha! Please, Try Again')
