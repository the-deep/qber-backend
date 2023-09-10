import strawberry
import datetime
from strawberry.types import Info
from django.db import models
from django.db.models.fields.files import FieldFile as DjFieldFile
from django.http import HttpRequest
from django.core.files.storage import FileSystemStorage, storages
from django.core.cache import cache
from django.conf import settings

from main.caches import local_cache, CacheKey
from apps.common.serializers import TempClientIdMixin
from apps.user.types import UserType


class ClientIdMixin:
    @strawberry.field
    def client_id(self, info: Info) -> strawberry.ID:
        self.id: int
        # NOTE: We should always provide non-null client_id
        return strawberry.ID(
            getattr(self, 'client_id', None) or
            local_cache.get(TempClientIdMixin.get_cache_key(self, info.context.request)) or
            str(self.id)
        )


class UserResourceTypeMixin:
    created_at: datetime.datetime
    modified_at: datetime.datetime

    @strawberry.field
    def created_by(self, info: Info) -> UserType:
        return info.context.dl.user.load_users.load(self.created_by_id)

    @strawberry.field
    def modified_by(self, info: Info) -> UserType:
        return info.context.dl.user.load_users.load(self.modified_by_id)


def get_cached_file_uri(file: DjFieldFile, request: HttpRequest) -> str | None:
    if file.name is None:
        return

    if isinstance(storages.backends['default'], FileSystemStorage):
        return request.build_absolute_uri(file.url)
    # Other is only S3 for now
    cache_key = CacheKey.URL_CACHED_FILE_FIELD_KEY_FORMAT.format(CacheKey.generate_hash(file.name))
    if url := cache.get(cache_key):
        return url
    cache.set(cache_key, file.url, settings.MEDIA_FILE_CACHE_URL_TTL)
    return file.url


@strawberry.type
class FileFieldType:
    @strawberry.field
    @staticmethod
    def name(root: DjFieldFile, _: Info) -> str:
        name = root.name
        return name  # pyright: ignore [reportGeneralTypeIssues]

    @strawberry.field
    @staticmethod
    def url(root: DjFieldFile, info: Info) -> str:
        return get_cached_file_uri(
            root,
            info.context.request,
        )  # pyright: ignore [reportGeneralTypeIssues]


def file_field(field):
    _field = field
    if isinstance(field, models.query_utils.DeferredAttribute):
        _field = field.field

    def _get_value(root) -> None | FileFieldType:
        file_obj = getattr(root, _field.attname)
        if file_obj.name:
            return file_obj

    @strawberry.field
    def field_(root, _: Info) -> FileFieldType:
        return _get_value(
            root,
        )   # pyright: ignore [reportGeneralTypeIssues]

    @strawberry.field
    def nullable_field_(root, _: Info) -> None | FileFieldType:
        return _get_value(root)

    if _field.null or _field.blank:
        return nullable_field_
    return field_


def user_field(field):
    _field = field
    if isinstance(field, models.query_utils.DeferredAttribute):
        _field = field.field

    def _get_value(root, info: Info) -> None | UserType:
        _user_id = getattr(root, _field.attname)
        if _user_id:
            return info.context.dl.user.load_users.load(_user_id)

    @strawberry.field
    def field_(root, info: Info) -> UserType:
        return _get_value(
            root,
            info
        )   # pyright: ignore [reportGeneralTypeIssues]

    @strawberry.field
    def nullable_field_(root, info: Info) -> None | UserType:
        return _get_value(root, info)

    if _field.null:
        return nullable_field_
    return field_
