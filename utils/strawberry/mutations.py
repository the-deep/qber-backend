import typing
import strawberry
import logging
from strawberry.utils.str_converters import to_camel_case
from strawberry.types import Info
from asgiref.sync import sync_to_async
from rest_framework import serializers
from django.db import transaction, models

from utils.common import to_snake_case
from utils.strawberry.transformers import generate_type_for_serializer
from apps.project.models import Project


logger = logging.getLogger(__name__)

ResultTypeVar = typing.TypeVar("ResultTypeVar")


ARRAY_NON_MEMBER_ERRORS = 'nonMemberErrors'

# generalize all the CustomErrorType
CustomErrorType = strawberry.scalar(
    typing.NewType("CustomErrorType", object),
    description="A generic type to return error messages",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


def process_input_data(data) -> dict:
    """
    Return dict from Strawberry Input Object
    """
    return {
        key: value
        for key, value in data.__dict__.items()
        if value != strawberry.UNSET
    }


@strawberry.type
class ArrayNestedErrorType:
    client_id: str
    messages: typing.Optional[str]
    object_errors: typing.Optional[list[typing.Optional[CustomErrorType]]]

    def keys(self):
        return ['client_id', 'messages', 'object_errors']

    def __getitem__(self, key):
        key = to_snake_case(key)
        if key in ('object_errors',) and getattr(self, key):
            return [dict(each) for each in getattr(self, key)]
        return getattr(self, key)


@strawberry.type
class _CustomErrorType:
    field: str
    client_id: str | None = None
    messages: typing.Optional[str]
    object_errors: typing.Optional[
        list[typing.Optional[CustomErrorType]]
    ]
    array_errors: typing.Optional[
        list[typing.Optional[ArrayNestedErrorType]]
    ]

    DEFAULT_ERROR_MESSAGE = (
        'Something unexpected has occured. '
        'Please contact an admin to fix this issue.'
    )

    @staticmethod
    def generate_message(message: str = DEFAULT_ERROR_MESSAGE) -> CustomErrorType:
        return CustomErrorType([
            dict(
                field='nonFieldErrors',
                messages=message,
                object_errors=None,
                array_errors=None,
            )
        ])

    def keys(self):
        return ['field', 'client_id', 'messages', 'object_errors', 'array_errors']

    def __getitem__(self, key):
        key = to_snake_case(key)
        if key in ('object_errors', 'array_errors') and getattr(self, key):
            return [dict(each) for each in getattr(self, key)]
        return getattr(self, key)


def serializer_error_to_error_types(errors: dict, initial_data: dict | None = None) -> list:
    initial_data = initial_data or dict()
    node_client_id = initial_data.get('client_id')
    error_types = list()
    for field, value in errors.items():
        if isinstance(value, dict):
            error_types.append(_CustomErrorType(
                client_id=node_client_id,
                field=to_camel_case(field),
                object_errors=value,
                array_errors=None,
                messages=None,
            ))
        elif isinstance(value, list):
            if isinstance(value[0], str):
                if isinstance(initial_data.get(field), list):
                    # we have found an array input with top level error
                    error_types.append(_CustomErrorType(
                        client_id=node_client_id,
                        field=to_camel_case(field),
                        array_errors=[ArrayNestedErrorType(
                            client_id=ARRAY_NON_MEMBER_ERRORS,
                            messages=''.join(str(msg) for msg in value),
                            object_errors=None,
                        )],
                        messages=None,
                        object_errors=None,
                    ))
                else:
                    error_types.append(_CustomErrorType(
                        client_id=node_client_id,
                        field=to_camel_case(field),
                        messages=', '.join(str(msg) for msg in value),
                        object_errors=None,
                        array_errors=None,
                    ))
            elif isinstance(value[0], dict):
                array_errors = []
                for pos, array_item in enumerate(value):
                    if not array_item:
                        # array item might not have error
                        continue
                    # fetch array.item.client_id from the initial data
                    array_client_id = initial_data[field][pos].get('client_id', f'NOT_FOUND_{pos}')
                    array_errors.append(ArrayNestedErrorType(
                        client_id=array_client_id,
                        object_errors=serializer_error_to_error_types(array_item, initial_data[field][pos]),
                        messages=None,
                    ))
                error_types.append(_CustomErrorType(
                    client_id=node_client_id,
                    field=to_camel_case(field),
                    array_errors=array_errors,
                    object_errors=None,
                    messages=None,
                ))
        else:
            # fallback
            error_types.append(_CustomErrorType(
                field=to_camel_case(field),
                messages=' '.join(str(msg) for msg in value),
                array_errors=None,
                object_errors=None,
            ))
    return error_types


def mutation_is_not_valid(serializer) -> CustomErrorType | None:
    """
    Checks if serializer is valid, if not returns list of errorTypes
    """
    if not serializer.is_valid():
        errors = serializer_error_to_error_types(serializer.errors, serializer.initial_data)
        return CustomErrorType([dict(each) for each in errors])
    return None


@strawberry.type
class MutationResponseType(typing.Generic[ResultTypeVar]):
    ok: bool = True
    errors: typing.Optional[CustomErrorType] = None
    result: typing.Optional[ResultTypeVar] = None


@strawberry.type
class BulkMutationResponseType(typing.Generic[ResultTypeVar]):
    errors: typing.Optional[list[CustomErrorType]] = None
    results: typing.Optional[list[ResultTypeVar]] = None
    deleted: typing.Optional[list[ResultTypeVar]] = None


@strawberry.type
class MutationEmptyResponseType():
    ok: bool = True
    errors: typing.Optional[CustomErrorType] = None


def get_serializer_context(info: Info):
    return {
        'graphql_info': info,
        'request': info.context.request,
        'active_project': info.context.active_project,
    }


class ModelMutation:
    InputType: type
    PartialInputType: type

    def __init__(
        self,
        name: str,
        serializer_class: typing.Type[serializers.Serializer],
    ):
        self.serializer_class = serializer_class
        # Generated types
        self.InputType = generate_type_for_serializer(
            name + 'CreateInput',
            self.serializer_class,
        )
        self.PartialInputType = generate_type_for_serializer(
            name + 'UpdateInput',
            self.serializer_class,
            partial=True,
        )

    def check_permissions(self, info, permission) -> CustomErrorType | None:
        if permission and not info.context.has_perm(permission):
            errors = CustomErrorType([
                dict(
                    field="nonFieldErrors",
                    messages="You don't have enough permission",
                    object_errors=None,
                    array_errors=None,
                )
            ])
            return errors

    @staticmethod
    @sync_to_async
    def handle_mutation(
        serializer_class,
        data,
        info,
        **kwargs,
    ) -> tuple[CustomErrorType | None, models.Model | None]:
        serializer = serializer_class(
            data=data,
            context=get_serializer_context(info),
            **kwargs,
        )
        if errors := mutation_is_not_valid(serializer):
            return errors, None
        try:
            with transaction.atomic():
                instance = serializer.save()
        except Exception:
            logger.error('Failed to handle mutation', exc_info=True)
            return _CustomErrorType.generate_message(), None
        return None, instance

    @staticmethod
    @sync_to_async
    def handle_delete(instance: models.Model) -> tuple[CustomErrorType | None, models.Model | None]:
        try:
            with transaction.atomic():
                old_id = instance.pk
                instance.delete()
                instance.pk = old_id
                return None, instance
        except Exception:
            logger.error('Failed to handle delete mutation', exc_info=True)
            return _CustomErrorType.generate_message(), None

    async def handle_create_mutation(self, data, info: Info, permission) -> MutationResponseType:
        if errors := self.check_permissions(info, permission):
            return MutationResponseType(ok=False, errors=errors)
        errors, saved_instance = await self.handle_mutation(
            self.serializer_class,
            process_input_data(data),
            info,
        )
        if errors:
            return MutationResponseType(ok=False, errors=errors)
        return MutationResponseType(result=saved_instance)

    async def handle_update_mutation(
        self,
        data,
        info: Info,
        permission,
        instance: models.Model,
    ) -> MutationResponseType:
        if errors := self.check_permissions(info, permission):
            return MutationResponseType(ok=False, errors=errors)
        errors, saved_instance = await self.handle_mutation(
            self.serializer_class,
            process_input_data(data),
            info,
            instance=instance,
            partial=True,
        )
        if errors:
            return MutationResponseType(ok=False, errors=errors)
        return MutationResponseType(result=saved_instance)

    async def handle_delete_mutation(self, instance: models.Model | None, info: Info, permission) -> MutationResponseType:
        if errors := self.check_permissions(info, permission):
            return MutationResponseType(ok=False, errors=errors)
        if instance is None:
            return MutationResponseType(
                ok=False,
                errors=_CustomErrorType.generate_message("Doesn't exists"),
            )
        errors, deleted_instance = await self.handle_delete(instance)
        if errors:
            return MutationResponseType(ok=False, errors=errors)
        return MutationResponseType(result=deleted_instance)

    async def handle_bulk_mutation(
        self,
        base_queryset: models.QuerySet,
        items: list | None,
        delete_ids: list[strawberry.ID] | None,
        info: Info,
        permission: Project.Permission,
    ) -> BulkMutationResponseType:
        if errors := self.check_permissions(info, permission):
            return BulkMutationResponseType(errors=[errors])

        errors = []

        # Delete - First
        deleted_instances = []
        delete_qs = base_queryset.filter(id__in=delete_ids)
        async for item in delete_qs.all():
            _errors, _saved_instance = await self.handle_delete(item)
            if _errors:
                errors.append(_errors)
            else:
                deleted_instances.append(_saved_instance)

        # Create/Update - Then
        results = []
        for data in items or []:
            _data = process_input_data(data)
            _id = _data.pop('id', None)
            instance = None
            if _id:
                instance = await base_queryset.filter(id=_id).afirst()
            partial = False
            if instance:
                partial = True
            _errors, _saved_instance = await self.handle_mutation(
                self.serializer_class,
                _data,
                info,
                instance=instance,
                partial=partial,
            )
            if _errors:
                errors.append(_errors)
            else:
                results.append(_saved_instance)

        return BulkMutationResponseType(
            errors=errors,
            # Data
            results=results,
            deleted=deleted_instances,
        )
