import strawberry

from strawberry.types import Info

from utils.strawberry.paginations import CountList, pagination_field

from apps.questionnaire import queries as questionnaire_queries
from apps.export import queries as export_queries

from .models import Project
from .types import ProjectType, ProjectOrder
from .filters import ProjectFilter


# NOTE: strawberry_django.type doesn't let use arguments in the field
@strawberry.type
class ProjectScopeType(
    questionnaire_queries.PrivateProjectQuery,
    export_queries.PrivateProjectQuery,
):
    id: strawberry.ID

    @strawberry.field
    def project(self, info: Info) -> ProjectType:
        return info.context.active_project.project


@strawberry.type
class PrivateQuery:
    projects: CountList[ProjectType] = pagination_field(
        pagination=True,
        filters=ProjectFilter,
        order=ProjectOrder,
    )

    @strawberry.field
    async def project_scope(self, info: Info, pk: strawberry.ID) -> ProjectScopeType | None:
        project = await Project\
            .get_for(info.context.request.user)\
            .filter(pk=pk)\
            .afirst()
        if project:
            await info.context.set_active_project(project)
        return project
