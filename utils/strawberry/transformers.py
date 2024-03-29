import typing
import strawberry
import dataclasses
import datetime
import decimal

from importlib import import_module
from collections import OrderedDict
from functools import singledispatch
from rest_framework import serializers, fields as drf_fields
from strawberry.field import StrawberryField
from strawberry.annotation import StrawberryAnnotation
from django.core.exceptions import ImproperlyConfigured

from main.enums import ENUM_TO_STRAWBERRY_ENUM_MAP

from .enums import get_enum_name_from_django_field
from .serializers import IntegerIDField, StringIDField
from . import types

from strawberry_django.type import get_field

"""
XXX:
- This is a experimental transformer which translates DRF -> Strawberry Input Type
- Also overwrites some modules
"""


@singledispatch
def get_strawberry_type_from_serializer_field(field):
    raise ImproperlyConfigured(
        "Don't know how to convert the serializer field %s (%s) "
        "to strawberry type" % (field, field.__class__)
    )


@get_strawberry_type_from_serializer_field.register(serializers.ListField)
@get_strawberry_type_from_serializer_field.register(serializers.ListSerializer)
@get_strawberry_type_from_serializer_field.register(serializers.MultipleChoiceField)
def convert_list_serializer_to_field(field):
    child_type = get_strawberry_type_from_serializer_field(field.child)
    if not field.child.required:
        return list[typing.Optional[child_type]]
    return list[child_type]


@get_strawberry_type_from_serializer_field.register(serializers.Serializer)
@get_strawberry_type_from_serializer_field.register(serializers.ModelSerializer)
def convert_serializer_to_field(_):
    return strawberry.field


@get_strawberry_type_from_serializer_field.register(serializers.ManyRelatedField)
def convert_serializer_field_to_many_related_id(_):
    return list[strawberry.ID]


@get_strawberry_type_from_serializer_field.register(serializers.PrimaryKeyRelatedField)
@get_strawberry_type_from_serializer_field.register(IntegerIDField)
@get_strawberry_type_from_serializer_field.register(StringIDField)
def convert_serializer_field_to_id(_):
    return strawberry.ID


@get_strawberry_type_from_serializer_field.register(serializers.JSONField)
@get_strawberry_type_from_serializer_field.register(serializers.DictField)
def convert_serializer_field_to_generic_scalar(_):
    return types.GenericScalar


@get_strawberry_type_from_serializer_field.register(serializers.Field)
def convert_serializer_field_to_string(_):
    return str


@get_strawberry_type_from_serializer_field.register(serializers.IntegerField)
def convert_serializer_field_to_int(_):
    return int


@get_strawberry_type_from_serializer_field.register(serializers.BooleanField)
def convert_serializer_field_to_bool(_):
    return bool


@get_strawberry_type_from_serializer_field.register(serializers.FloatField)
def convert_serializer_field_to_float(_):
    return float


@get_strawberry_type_from_serializer_field.register(serializers.DecimalField)
def convert_serializer_field_to_decimal(_):
    return decimal.Decimal


@get_strawberry_type_from_serializer_field.register(serializers.DateTimeField)
def convert_serializer_field_to_datetime_time(_):
    return datetime.datetime


@get_strawberry_type_from_serializer_field.register(serializers.DateField)
def convert_serializer_field_to_date_time(_):
    return datetime.date


@get_strawberry_type_from_serializer_field.register(serializers.TimeField)
def convert_serializer_field_to_time(_):
    return datetime.time


@get_strawberry_type_from_serializer_field.register(serializers.ChoiceField)
def convert_serializer_field_to_enum(field):
    # Try normal TextChoices/IntegerChoices enum
    custom_name = get_enum_name_from_django_field(field)
    if custom_name not in ENUM_TO_STRAWBERRY_ENUM_MAP:
        # Try django_enumfield (NOTE: Let's try to avoid this)
        custom_name = type(list(field.choices.values())[-1]).__name__
    if custom_name is None:
        raise Exception(f'Enum name generation failed for {field=}')
    return ENUM_TO_STRAWBERRY_ENUM_MAP[custom_name]


def convert_serializer_to_type(serializer_class):
    """
    graphene_django.rest_framework.serializer_converter.convert_serializer_to_type
    """
    cached_type = convert_serializer_to_type.cache.get(
        serializer_class.__name__, None
    )
    if cached_type:
        return cached_type
    serializer = serializer_class()

    items = {
        name: convert_serializer_field(field)
        for name, field in serializer.fields.items()
    }
    # Alter naming
    serializer_name = serializer.__class__.__name__
    serializer_name = ''.join(''.join(serializer_name.split('ModelSerializer')).split('Serializer'))
    ref_name = f'{serializer_name}Type'

    ret_type = type(
        ref_name,
        (),
        items,
    )
    convert_serializer_to_type.cache[serializer_class.__name__] = ret_type
    return ret_type


convert_serializer_to_type.cache = {}


def convert_serializer_field(field, convert_choices_to_enum=True, force_optional=False):
    """
    Converts a django rest frameworks field to a graphql field
    and marks the field as required if we are creating an type
    and the field itself is required
    """

    if isinstance(field, serializers.ChoiceField) and not convert_choices_to_enum:
        graphql_type = str
    else:
        graphql_type = get_strawberry_type_from_serializer_field(field)

    kwargs = {
        "description": field.help_text,  # XXX: NOT WORKING
        "python_name": field.field_name,
        "graphql_name": field.field_name,
    }
    is_required = field.required and not force_optional
    if field.default != drf_fields.empty:
        if field.default.__class__.__hash__ is None:  # Mutable
            kwargs['default_factory'] = lambda: field.default
        else:
            kwargs['default'] = field.default
    else:
        kwargs['default'] = dataclasses.MISSING

    # if it is a tuple or a list it means that we are returning
    # the graphql type and the child type
    if isinstance(graphql_type, (list, tuple)):
        kwargs["of_type"] = graphql_type[1]
        graphql_type = graphql_type[0]

    if isinstance(field, serializers.Serializer):
        pass
    elif isinstance(field, serializers.ListSerializer):
        field = field.child
        kwargs["of_type"] = convert_serializer_to_type(field.__class__)

    if not is_required:
        if 'default' not in kwargs or 'default_factory' not in kwargs:
            kwargs['default'] = strawberry.UNSET
        graphql_type = typing.Optional[graphql_type]

    return graphql_type, StrawberryField(
        type_annotation=StrawberryAnnotation(
            annotation=graphql_type,
        ),
        **kwargs,
    )


def fields_for_serializer(
    serializer,
    only_fields,
    exclude_fields,
    convert_choices_to_enum=True,
    partial=False,
):
    """
    NOTE: Same as the original definition. Needs overriding to
    handle relative import of convert_serializer_field
    """
    fields = OrderedDict()
    for name, field in serializer.fields.items():
        is_not_in_only = only_fields and name not in only_fields
        is_excluded = name in exclude_fields
        if is_not_in_only or is_excluded:
            continue
        fields[name] = convert_serializer_field(
            field,
            convert_choices_to_enum=convert_choices_to_enum,
            force_optional=partial,
        )
    return fields


def generate_type_for_serializer(
    name: str,
    serializer_class,
    partial=False,
) -> type:
    data_members = fields_for_serializer(
        serializer_class(),
        only_fields=[],
        exclude_fields=[],
        partial=partial,
    )
    defaults_model_fields = [
        (name, _type, field)
        for name, (_type, field) in data_members.items()
        if (field.default is not dataclasses.MISSING or field.default_factory is not dataclasses.MISSING)
    ]
    non_defaults_model_fields = [
        (name, _type, field)
        for name, (_type, field) in data_members.items()
        if (field.default is dataclasses.MISSING and field.default_factory is dataclasses.MISSING)
    ]
    return strawberry.input(
        dataclasses.make_dataclass(
            name,
            [
                *non_defaults_model_fields,
                *defaults_model_fields,
            ]
        )
    )


class MonkeyPatch:
    og_get_field = get_field

    @classmethod
    def get_field_monkey_patch(
        cls,
        django_type,
        field_name: str,
        field_annotation: StrawberryAnnotation | None = None,
    ):
        """
        For field with <field>_id, let's use ID instead of object while rendering.
        For eg:
            For field: `member_id: strawberry.ID`, where `member` is a ForeignKey
                Previous behaviour:
                    member_id gives value "Member object (1)" == str(obj.member)
                New behaviour:
                    member_id gives value "1" == str(obj.member_id)
        NOTE: This doesn't work with Mixin
        """
        field = cls.og_get_field(
            django_type,
            field_name,
            field_annotation,
        )
        # CUSTOM CHANGE -- START
        if field_name.endswith('_id'):
            field.django_name = field_name
        return field
        # CUSTOM CHANGE -- END


import_module('strawberry_django.type').get_field = MonkeyPatch.get_field_monkey_patch
