import strawberry
import datetime
from strawberry.types import Info

from main.caches import local_cache
from apps.common.serializers import TempClientIdMixin
from apps.user.types import UserType


class ClientIdMixin:

    @strawberry.field
    def client_id(self, info: Info) -> str:
        self.id: int
        # NOTE: We should always provide non-null client_id
        return (
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
