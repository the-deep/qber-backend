import strawberry
import strawberry_django
from strawberry.types import Info

from asgiref.sync import sync_to_async
from utils.strawberry.paginations import CountList, pagination_field

from .types import UserType, UserMeType
from .filters import UserFilter


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

    users: CountList[UserType] = pagination_field(
        pagination=True,
        filters=UserFilter,
    )
