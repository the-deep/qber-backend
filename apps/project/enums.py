import strawberry

from utils.strawberry.enums import get_enum_name_from_django_field

from .models import Project, ProjectMembership

ProjectPermissionTypeEnum = strawberry.enum(Project.Permission, name='ProjectPermissionTypeEnum')
ProjectMembershipRoleTypeEnum = strawberry.enum(ProjectMembership.Role, name='ProjectMembershipRoleTypeEnum')


enum_map = {
    get_enum_name_from_django_field(field): enum
    for field, enum in (
        (ProjectMembership.role, ProjectMembershipRoleTypeEnum),
    )
}
