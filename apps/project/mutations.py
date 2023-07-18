import strawberry
from strawberry.types import Info

from utils.strawberry.mutations import (
    MutationResponseType,
    BulkMutationResponseType,
    MutationEmptyResponseType,
    ModelMutation,
    _CustomErrorType,
)

from apps.questionnaire import mutations as questionnaire_mutations
from .models import Project, ProjectMembership
from .serializers import (
    ProjectSerializer,
    ProjectMembershipBulkSerializer,
)
from .types import ProjectType, ProjectMembershipType

ProjectMutation = ModelMutation('Project', ProjectSerializer)
ProjectMembershipBulkMutation = ModelMutation('ProjectMembership', ProjectMembershipBulkSerializer)


# NOTE: strawberry_django.type doesn't let use arguments in the field
@strawberry.type
class ProjectScopeMutation(
    questionnaire_mutations.ProjectScopeMutation,
):
    id: strawberry.ID

    @strawberry.mutation
    async def update_project(
        self,
        data: ProjectMutation.PartialInputType,
        info: Info,
    ) -> MutationResponseType[ProjectType]:
        return await ProjectMutation.handle_update_mutation(
            data,
            info,
            Project.Permission.UPDATE_PROJECT,
            info.context.active_project.project,
        )

    @strawberry.mutation
    async def leave_project(
        self,
        confirm_password: str,
        info: Info,
    ) -> MutationEmptyResponseType:
        user = info.context.request.user
        if not user.check_password(confirm_password):
            return MutationEmptyResponseType(
                ok=False,
                errors=_CustomErrorType.generate_message("Password didn't match"),
            )
        queryset = ProjectMembership.objects.filter(
            project=info.context.active_project.project,
            member=info.context.request.user,
        )
        # Delete membership
        await queryset.adelete()
        return MutationEmptyResponseType(ok=True)

    @strawberry.mutation
    async def update_memberships(
        self,
        items: list[ProjectMembershipBulkMutation.PartialInputType] | None,
        delete_ids: list[strawberry.ID] | None,
        info: Info,
    ) -> BulkMutationResponseType[ProjectMembershipType]:
        queryset = ProjectMembership.objects.filter(
            project=info.context.active_project.project,
        ).exclude(member=info.context.request.user)
        return await ProjectMembershipBulkMutation.handle_bulk_mutation(
            queryset,
            items,
            delete_ids,
            info,
            Project.Permission.UPDATE_MEMBERSHIPS,
        )


@strawberry.type
class PrivateMutation:
    @strawberry.mutation
    async def create_project(
        self,
        data: ProjectMutation.InputType,
        info: Info,
    ) -> MutationResponseType[ProjectType]:
        response = await ProjectMutation.handle_create_mutation(
            data,
            info,
            None,
        )
        if response.ok:
            await info.context.set_active_project(response.result)
        return response

    @strawberry.field
    async def project_scope(self, info: Info, pk: strawberry.ID) -> ProjectScopeMutation | None:
        project = await Project\
            .get_for(info.context.request.user)\
            .filter(pk=pk)\
            .afirst()
        if project:
            await info.context.set_active_project(project)
        return project
