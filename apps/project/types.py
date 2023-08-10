import typing
import strawberry
import strawberry_django
from strawberry.types import Info
from asgiref.sync import sync_to_async

from utils.common import get_queryset_for_model
from utils.strawberry.paginations import CountList, pagination_field
from apps.common.types import ClientIdMixin, UserResourceTypeMixin
from apps.user.types import UserType

from .models import Project, ProjectMembership
from .filters import ProjectMembershipFilter
from .enums import ProjectMembershipRoleTypeEnum, ProjectPermissionTypeEnum


@strawberry_django.ordering.order(ProjectMembership)
class ProjectMembershipOrder:
    id: strawberry.auto
    joined_at: strawberry.auto


@strawberry_django.type(ProjectMembership)
class ProjectMembershipType(ClientIdMixin):
    id: strawberry.ID
    role: ProjectMembershipRoleTypeEnum
    joined_at: strawberry.auto

    member_id: strawberry.ID
    added_by_id: strawberry.ID | None

    def get_queryset(self, queryset, info: Info):
        queryset = get_queryset_for_model(ProjectMembership, queryset=queryset)
        if info.context.active_project is None:
            raise Exception('members field is not allowed for project listing.')
        return queryset.filter(
            project=info.context.active_project.project,
        )

    @strawberry.field
    def member(self, info: Info) -> UserType:
        return info.context.dl.user.load_users.load(self.member_id)

    @strawberry.field
    def added_by(self, info: Info) -> UserType | None:
        if self.added_by_id:
            return info.context.dl.user.load_users.load(self.added_by_id)


@strawberry_django.ordering.order(Project)
class ProjectOrder:
    id: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.type(Project)
class ProjectType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto

    members: CountList[ProjectMembershipType] = pagination_field(
        pagination=True,
        filters=ProjectMembershipFilter,
        order=ProjectMembershipOrder,
    )

    @strawberry.field
    def current_user_role(self) -> typing.Optional[ProjectMembershipRoleTypeEnum]:
        # Annotated by Project.get_for
        return getattr(self, 'current_user_role', None)

    @strawberry.field
    @sync_to_async
    def allowed_permissions(self, info: Info) -> list[ProjectPermissionTypeEnum]:
        # TODO: Use dataloader
        return self.get_permissions_for_user(info.context.request.user)

    def get_queryset(self, queryset, info: Info):
        return Project.get_for(
            info.context.request.user,
            queryset=queryset,
        )
