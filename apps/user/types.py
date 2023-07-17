import strawberry
import strawberry_django
from .models import User
from .enums import OptEmailNotificationTypeEnum


@strawberry_django.type(User)
class UserType:
    id: strawberry.ID
    first_name: strawberry.auto
    last_name: strawberry.auto

    @strawberry.field
    def display_name(self) -> str:
        return self.get_full_name()


@strawberry_django.type(User)
class UserMeType(UserType):
    email: strawberry.auto
    email_opt_outs: list[OptEmailNotificationTypeEnum]
