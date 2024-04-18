import strawberry
from asgiref.sync import sync_to_async
from dataclasses import dataclass
from strawberry.django.views import AsyncGraphQLView
from strawberry.django.context import StrawberryDjangoContext

# Imported to make sure strawberry custom modules are loadded first
import utils.strawberry.transformers  # noqa: 403

from main.enums import AppEnumCollection, AppEnumCollectionData
from apps.project.models import Project
from apps.common.enums import GlobalPermissionTypeEnum
from apps.user.models import User

from apps.user import queries as user_queries, mutations as user_mutations
from apps.project import queries as project_queries
from apps.project import mutations as project_mutations
from apps.qbank import queries as qbank_queries, mutations as qbank_mutations

from .permissions import IsAuthenticated
from .dataloaders import GlobalDataLoader


@dataclass
class ProjectContext:
    project: Project
    permissions: set[Project.Permission]


@dataclass
class GraphQLContext(StrawberryDjangoContext):
    dl: GlobalDataLoader
    global_permissions: set[GlobalPermissionTypeEnum]
    active_project: ProjectContext | None = None

    @sync_to_async
    def set_active_project(self, project: Project):
        if self.active_project is not None:
            if self.active_project.project.id == project.id:
                return
            raise Exception('Alias for project node is not allowed! Please use seperate request')
        if self.request.user.is_anonymous:
            raise Exception('User should be logged in')
        permissions = project.get_permissions_for_user(self.request.user)
        self.active_project = ProjectContext(
            project=project,
            permissions=set(permissions)
        )

    def has_perm(self, permission: Project.Permission):
        if self.active_project is None:
            raise Exception('There is no active project to select permissions from.')
        return permission in self.active_project.permissions

    def has_global_perm(self, permission) -> str | None:
        if permission not in self.global_permissions:
            return f"You don't have permission for {permission.label}"


class CustomAsyncGraphQLView(AsyncGraphQLView):
    @staticmethod
    @sync_to_async
    def get_global_permissions(user: User) -> set[GlobalPermissionTypeEnum]:
        if not user.is_anonymous:
            return user.get_global_permissions()
        return set()

    async def get_context(self, request, **kwargs) -> GraphQLContext:
        global_permissions = await self.get_global_permissions(request.user)
        return GraphQLContext(
            request,
            **kwargs,
            global_permissions=global_permissions,
            dl=GlobalDataLoader(),
        )


@strawberry.type
class PublicQuery(
    user_queries.PublicQuery,
):
    id: strawberry.ID = strawberry.ID('public')


@strawberry.type
class PrivateQuery(
    user_queries.PrivateQuery,
    project_queries.PrivateQuery,
    qbank_queries.PrivateQuery,
    # questionnaire_queries.PrivateQuery,
):
    id: strawberry.ID = strawberry.ID('private')


@strawberry.type
class PublicMutation(
    user_mutations.PublicMutation,
):
    id: strawberry.ID = strawberry.ID('public')


@strawberry.type
class PrivateMutation(
    user_mutations.PrivateMutation,
    qbank_mutations.PrivateMutation,
    project_mutations.PrivateMutation,
):
    id: strawberry.ID = strawberry.ID('private')


@strawberry.type
class Query:
    public: PublicQuery = strawberry.field(
        resolver=lambda: PublicQuery()
    )
    private: PrivateQuery = strawberry.field(
        permission_classes=[IsAuthenticated],
        resolver=lambda: PrivateQuery()
    )
    enums: AppEnumCollection = strawberry.field(
        resolver=lambda: AppEnumCollectionData()
    )


@strawberry.type
class Mutation:
    public: PublicMutation = strawberry.field(resolver=lambda: PublicMutation())
    private: PrivateMutation = strawberry.field(
        resolver=lambda: PrivateMutation(),
        permission_classes=[IsAuthenticated],
    )


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
