import strawberry
from strawberry.types import Info

from utils.strawberry.mutations import (
    MutationResponseType,
    ModelMutation,
)
from utils.common import get_object_or_404_async
from apps.project.models import Project

from .serializers import QuestionnaireExportSerializer
from .types import QuestionnaireExportType

QuestionnaireExportMutation = ModelMutation('QuestionnaireExport', QuestionnaireExportSerializer)


@strawberry.type
class ProjectScopeMutation:
    @strawberry.mutation
    async def create_questionnaire_export(
        self,
        data: QuestionnaireExportMutation.InputType,
        info: Info,
    ) -> MutationResponseType[QuestionnaireExportType]:
        return await QuestionnaireExportMutation.handle_create_mutation(
            data,
            info,
            Project.Permission.CREATE_QUESTION_CHOICE,
        )

    @strawberry.mutation
    async def delete_questionnaire_export(
        self,
        id: strawberry.ID,
        info: Info,
    ) -> MutationResponseType[QuestionnaireExportType]:
        queryset = QuestionnaireExportType.get_queryset(None, None, info)
        return await QuestionnaireExportMutation.handle_delete_mutation(
            await get_object_or_404_async(queryset, id=id),
            info,
            Project.Permission.DELETE_QUESTION_CHOICE,
        )
