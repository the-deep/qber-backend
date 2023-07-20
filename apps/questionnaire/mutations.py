import strawberry
from strawberry.types import Info

from utils.strawberry.mutations import MutationResponseType, ModelMutation

from .models import Project
from .serializers import (
    QuestionnaireSerializer,
)
from .types import QuestionnaireType

QuestionnaireMutation = ModelMutation('Questionnaire', QuestionnaireSerializer)


# NOTE: strawberry_django.type doesn't let use arguments in the field
@strawberry.type
class ProjectScopeMutation():
    id: strawberry.ID

    @strawberry.mutation
    async def create_questionnaire(
        self,
        data: QuestionnaireMutation.InputType,
        info: Info,
    ) -> MutationResponseType[QuestionnaireType]:
        return await QuestionnaireMutation.handle_create_mutation(
            data,
            info,
            Project.Permission.CREATE_QUESTIONNAIRE,
        )

    @strawberry.mutation
    async def update_questionnaire(
        self,
        data: QuestionnaireMutation.PartialInputType,
        info: Info,
    ) -> MutationResponseType[QuestionnaireType]:
        return await QuestionnaireMutation.handle_update_mutation(
            data,
            info,
            Project.Permission.UPDATE_QUESTIONNAIRE,
            info.context.active_project.project,
        )

    @strawberry.mutation
    async def delete_questionnaire(
        self,
        id: strawberry.ID,
        info: Info,
    ) -> MutationResponseType[list[QuestionnaireType]]:
        queryset = QuestionnaireType.get_queryset(None, None, info)
        return await QuestionnaireMutation.handle_delete_mutation(
            queryset.filter(id=id).first(),
            info,
            Project.Permission.DELETE_QUESTIONNAIRE,
        )
