import typing
import strawberry
import strawberry_django
from strawberry.types import Info

from utils.common import get_queryset_for_model
from utils.strawberry.paginations import CountList, pagination_field
from apps.common.types import ClientIdMixin, UserResourceTypeMixin

from .models import Project, ProjectMembership
from .filters import ProjectMembershipFilter
from .enums import ProjectMembershipRoleTypeEnum


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

    def get_queryset(self, queryset, info: Info):
        return Project.get_for(
            info.context.request.user,
            queryset=queryset,
        )
