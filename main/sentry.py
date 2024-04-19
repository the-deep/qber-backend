import sentry_sdk
from django.conf import settings
from strawberry.permission import BasePermission
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import ignore_logger

IGNORED_ERRORS = [
    BasePermission,
]
IGNORED_LOGGERS = [
    "graphql.execution.utils",
    "CSSUTILS",
]

for _logger in IGNORED_LOGGERS:
    ignore_logger(_logger)


def before_send(event, hint):
    if 'exc_info' in hint:
        exc_type, exc_value, _ = hint['exc_info']
        # Ignore 'User is not authenticated' error message
        if (
            issubclass(exc_type, PermissionError) and
            str(exc_value) == 'User is not authenticated'
        ):
            return
    return event


def init_sentry(app_type, tags={}, **config):
    integrations = [
        DjangoIntegration(),
        CeleryIntegration(),
        RedisIntegration(),
    ]
    sentry_sdk.init(
        **config,
        traces_sample_rate=settings.SENTRY_SAMPLE_RATE,
        ignore_errors=IGNORED_ERRORS,
        integrations=integrations,
        before_send=before_send,
    )
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("app_type", app_type)
        for tag, value in tags.items():
            scope.set_tag(tag, value)
