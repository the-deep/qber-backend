import re
import copy
import typing
from asgiref.sync import sync_to_async
from user_agents import parse
from django.db import models
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404


# Adapted from this response in Stackoverflow
# http://stackoverflow.com/a/19053800/1072990
def to_camel_case(snake_str):
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'capitalize' method and join them together.
    return components[0] + "".join(x.capitalize() if x else "_" for x in components[1:])


# From this response in Stackoverflow
# http://stackoverflow.com/a/1176023/1072990
def to_snake_case(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_type(request):
    http_agent = request.META.get('HTTP_USER_AGENT')
    if http_agent:
        user_agent = parse(http_agent)
        return user_agent.browser.family + ',' + user_agent.os.family
    return


def get_queryset_for_model(
    model: typing.Type[models.Model],
    queryset: models.QuerySet | None = None,
) -> models.QuerySet:
    if queryset is not None:
        return copy.deepcopy(queryset)
    return model.objects.all()


def validate_xlsform_name(name):
    """
    Validate Name
    Names can only contain letters, digits, hyphens, underscores, and periods.
    Names are case-sensitive.
    """
    pattern = r'^[a-zA-Z0-9_\-\.]+$'
    if not bool(re.match(pattern, name)):
        raise ValidationError(
            (
                "%(name)s is not an valid name."
                " Names can only contain letters, digits, hyphens, underscores, and periods."
                " Names are case-sensitive."
            ),
            params={"name": name}
        )


@sync_to_async
def get_object_or_404_async(queryset, **kwargs):
    return get_object_or_404(queryset, **kwargs)
