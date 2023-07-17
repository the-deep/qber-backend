import strawberry
import strawberry_django
from strawberry.types import Info

from asgiref.sync import sync_to_async

from .types import UserType, UserMeType


@strawberry.type
class PublicQuery:
    @strawberry.field
    @sync_to_async
    def me(self, info: Info) -> UserMeType | None:
        user = info.context.request.user
        if user.is_authenticated:
            return user


@strawberry.type
class PrivateQuery:
    user: UserType = strawberry_django.field()
