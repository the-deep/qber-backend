import strawberry

from utils.strawberry.enums import get_enum_name_from_django_field

from .models import GlobalPermission

GlobalPermissionTypeEnum = strawberry.enum(GlobalPermission.Type, name='GlobalPermissionTypeEnum')


enum_map = {
    get_enum_name_from_django_field(field): enum
    for field, enum in (
        (GlobalPermission.type, GlobalPermissionTypeEnum),
    )
}
