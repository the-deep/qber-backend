import strawberry
from strawberry.types import Info

from utils.strawberry.mutations import MutationResponseType, ModelMutation
from utils.common import get_object_or_404_async

from .models import Project
from .serializers import (
    QuestionnaireSerializer,
    QuestionSerializer,
)
from .types import QuestionnaireType, QuestionType

QuestionnaireMutation = ModelMutation('Questionnaire', QuestionnaireSerializer)
QuestionMutation = ModelMutation('Question', QuestionSerializer)


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
        id: strawberry.ID,
        data: QuestionnaireMutation.PartialInputType,
        info: Info,
    ) -> MutationResponseType[QuestionnaireType]:
        queryset = QuestionnaireType.get_queryset(None, None, info)
        return await QuestionnaireMutation.handle_update_mutation(
            data,
            info,
            Project.Permission.UPDATE_QUESTIONNAIRE,
            await get_object_or_404_async(queryset, id=id),
        )

    @strawberry.mutation
    async def delete_questionnaire(
        self,
        id: strawberry.ID,
        info: Info,
    ) -> MutationResponseType[QuestionnaireType]:
        queryset = QuestionnaireType.get_queryset(None, None, info)
        return await QuestionnaireMutation.handle_delete_mutation(
            await get_object_or_404_async(queryset, id=id),
            info,
            Project.Permission.DELETE_QUESTIONNAIRE,
        )

    @strawberry.mutation
    async def create_question(
        self,
        data: QuestionMutation.InputType,
        info: Info,
    ) -> MutationResponseType[QuestionType]:
        return await QuestionMutation.handle_create_mutation(
            data,
            info,
            Project.Permission.CREATE_QUESTION,
        )

    @strawberry.mutation
    async def update_question(
        self,
        id: strawberry.ID,
        data: QuestionMutation.PartialInputType,
        info: Info,
    ) -> MutationResponseType[QuestionType]:
        queryset = QuestionType.get_queryset(None, None, info)
        return await QuestionMutation.handle_update_mutation(
            data,
            info,
            Project.Permission.UPDATE_QUESTION,
            await get_object_or_404_async(queryset, id=id),
        )

    @strawberry.mutation
    async def delete_question(
        self,
        id: strawberry.ID,
        info: Info,
    ) -> MutationResponseType[QuestionType]:
        queryset = QuestionType.get_queryset(None, None, info)
        return await QuestionMutation.handle_delete_mutation(
            await get_object_or_404_async(queryset, id=id),
            info,
            Project.Permission.DELETE_QUESTION,
        )
