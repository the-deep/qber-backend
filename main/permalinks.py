from django.conf import settings


class Permalink:
    BASE_URL = f'{settings.APP_HTTP_PROTOCOL}://{settings.APP_FRONTEND_HOST}/permalink'

    FORGOT_PASSWORD = f'{BASE_URL}/forgot-password'

    @classmethod
    def password_reset(cls, uid: str, token: str):
        return f'{cls.BASE_URL}/password-reset/{uid}/{token}'
