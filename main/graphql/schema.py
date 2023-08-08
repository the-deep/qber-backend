import strawberry
from asgiref.sync import sync_to_async
from dataclasses import dataclass
from strawberry.django.views import AsyncGraphQLView
from strawberry.django.context import StrawberryDjangoContext

import utils.strawberry.transformers  # noqa: 403

from apps.project.models import Project

from apps.user import queries as user_queries, mutations as user_mutations
from apps.project import queries as project_queries
from apps.project import mutations as project_mutations
# from apps.questionnaire import queries as questionnaire_queries

from .permissions import IsAuthenticated
from .dataloaders import GlobalDataLoader


@dataclass
class ProjectContext:
    project: Project
    permissions: set[Project.Permission]


@dataclass
class GraphQLContext(StrawberryDjangoContext):
    dl: GlobalDataLoader
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


class CustomAsyncGraphQLView(AsyncGraphQLView):
    async def get_context(self, *args, **kwargs) -> GraphQLContext:
        return GraphQLContext(
            *args,
            **kwargs,
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
