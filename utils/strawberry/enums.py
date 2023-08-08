from django.db import models
from django.contrib.postgres.fields import ArrayField
from rest_framework import serializers

from utils.common import to_camel_case


def get_enum_name_from_django_field(
    field: (
        None |
        serializers.ChoiceField |
        models.CharField |
        models.IntegerField |
        models.SmallIntegerField |
        ArrayField |
        models.query_utils.DeferredAttribute
    ),
    field_name=None,
    model_name=None,
    serializer_name=None,
):
    def _have_model(_field):
        if hasattr(_field, 'model') or hasattr(getattr(_field, 'Meta', None), 'model'):
            return True

    def _get_serializer_name(_field):
        if hasattr(_field, 'parent'):
            return type(_field.parent).__name__

    if field_name is None or model_name is None:
        if isinstance(field, models.query_utils.DeferredAttribute):
            return get_enum_name_from_django_field(
                field.field,
                field_name=field_name,
                model_name=model_name,
                serializer_name=serializer_name,
            )
        if isinstance(field, serializers.ChoiceField):
            if isinstance(field.parent, serializers.ListField):
                if _have_model(field.parent.parent):
                    model_name = model_name or field.parent.parent.Meta.model.__name__
                serializer_name = _get_serializer_name(field.parent)
                field_name = field_name or field.parent.field_name
            else:
                if _have_model(field.parent):
                    model_name = model_name or field.parent.Meta.model.__name__
                serializer_name = _get_serializer_name(field)
                field_name = field_name or field.field_name
        elif isinstance(field, ArrayField):
            if _have_model(field):
                model_name = model_name or field.model.__name__
            serializer_name = _get_serializer_name(field)
            field_name = field_name or field.base_field.name
        elif isinstance(field, (
            models.CharField,
            models.SmallIntegerField,
            models.IntegerField,
            models.PositiveSmallIntegerField,
        )):
            if _have_model(field):
                model_name = model_name or field.model.__name__
            serializer_name = _get_serializer_name(field)
            field_name = field_name or field.name
    if field_name is None:
        raise Exception(f'{field=} should have a name')
    if model_name:
        return f'{model_name}{to_camel_case(field_name.title())}'
    if serializer_name:
        return f'{serializer_name}{to_camel_case(field_name.title())}'
    raise Exception(f'{serializer_name=} should have a value')
