import strawberry
import strawberry_django

from utils.strawberry.enums import enum_field, enum_display_field

from .models import User


@strawberry_django.ordering.order(User)
class UserOrder:
    id: strawberry.auto


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
    email_opt_outs = enum_field(User.email_opt_outs)
    email_opt_outs_display = enum_display_field(User.email_opt_outs)
