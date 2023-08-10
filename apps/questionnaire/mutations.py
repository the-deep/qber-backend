import strawberry
from strawberry.types import Info

from utils.strawberry.mutations import MutationResponseType, ModelMutation
from utils.common import get_object_or_404_async

from .models import Project
from .serializers import (
    QuestionnaireSerializer,
    QuestionSerializer,
    QuestionGroupSerializer,
    QuestionChoiceCollectionSerializer,
)
from .types import (
    QuestionnaireType,
    QuestionType,
    QuestionGroupType,
    QuestionChoiceCollectionType,
)

QuestionnaireMutation = ModelMutation('Questionnaire', QuestionnaireSerializer)
QuestionMutation = ModelMutation('Question', QuestionSerializer)
QuestionGroupMutation = ModelMutation('QuestionGroup', QuestionGroupSerializer)
QuestionChoiceCollectionMutation = ModelMutation('QuestionChoiceCollection', QuestionChoiceCollectionSerializer)


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
            Project.Permission.DELETE_QUESTION_GROUP,
        )

    @strawberry.mutation
    async def create_question_group(
        self,
        data: QuestionGroupMutation.InputType,
        info: Info,
    ) -> MutationResponseType[QuestionGroupType]:
        return await QuestionGroupMutation.handle_create_mutation(
            data,
            info,
            Project.Permission.CREATE_QUESTION_GROUP,
        )

    @strawberry.mutation
    async def update_question_group(
        self,
        id: strawberry.ID,
        data: QuestionGroupMutation.PartialInputType,
        info: Info,
    ) -> MutationResponseType[QuestionGroupType]:
        queryset = QuestionGroupType.get_queryset(None, None, info)
        return await QuestionGroupMutation.handle_update_mutation(
            data,
            info,
            Project.Permission.UPDATE_QUESTION_GROUP,
            await get_object_or_404_async(queryset, id=id),
        )

    @strawberry.mutation
    async def delete_question_group(
        self,
        id: strawberry.ID,
        info: Info,
    ) -> MutationResponseType[QuestionGroupType]:
        queryset = QuestionGroupType.get_queryset(None, None, info)
        return await QuestionGroupMutation.handle_delete_mutation(
            await get_object_or_404_async(queryset, id=id),
            info,
            Project.Permission.DELETE_QUESTION_GROUP,
        )

    @strawberry.mutation
    async def create_question_choice_collection(
        self,
        data: QuestionChoiceCollectionMutation.InputType,
        info: Info,
    ) -> MutationResponseType[QuestionChoiceCollectionType]:
        return await QuestionChoiceCollectionMutation.handle_create_mutation(
            data,
            info,
            Project.Permission.CREATE_QUESTION_CHOICE,
        )

    @strawberry.mutation
    async def update_question_choice_collection(
        self,
        id: strawberry.ID,
        data: QuestionChoiceCollectionMutation.PartialInputType,
        info: Info,
    ) -> MutationResponseType[QuestionChoiceCollectionType]:
        queryset = QuestionChoiceCollectionType.get_queryset(None, None, info)
        return await QuestionChoiceCollectionMutation.handle_update_mutation(
            data,
            info,
            Project.Permission.UPDATE_QUESTION_CHOICE,
            await get_object_or_404_async(queryset, id=id),
        )

    @strawberry.mutation
    async def delete_question_choice_collection(
        self,
        id: strawberry.ID,
        info: Info,
    ) -> MutationResponseType[QuestionChoiceCollectionType]:
        queryset = QuestionChoiceCollectionType.get_queryset(None, None, info)
        return await QuestionChoiceCollectionMutation.handle_delete_mutation(
            await get_object_or_404_async(queryset, id=id),
            info,
            Project.Permission.DELETE_QUESTION_CHOICE,
        )
