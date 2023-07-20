from django.conf import settings


def app_environment(request):
    return {
        'request': request,
        'APP_ENVIRONMENT': settings.APP_ENVIRONMENT,
    }
