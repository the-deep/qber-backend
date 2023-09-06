import strawberry
from strawberry.types import Info
from asgiref.sync import sync_to_async

from utils.strawberry.mutations import (
    MutationResponseType,
    ModelMutation,
    BulkBasicMutationResponseType,
    process_input_data,
)
from utils.strawberry.transformers import convert_serializer_to_type
from utils.common import get_object_or_404_async

from .models import Project, QuestionLeafGroup, Question
from .serializers import (
    QuestionnaireSerializer,
    QuestionSerializer,
    QuestionChoiceCollectionSerializer,
    QuestionLeafGroupOrderSerializer,
    QuestionOrderSerializer,
)
from .types import (
    QuestionnaireType,
    QuestionType,
    QuestionLeafGroupType,
    QuestionChoiceCollectionType,
)
from .enums import VisibilityActionEnum

QuestionnaireMutation = ModelMutation('Questionnaire', QuestionnaireSerializer)
QuestionMutation = ModelMutation('Question', QuestionSerializer)
QuestionChoiceCollectionMutation = ModelMutation('QuestionChoiceCollection', QuestionChoiceCollectionSerializer)
QuestionLeafGroupOrderInputType = convert_serializer_to_type(
    QuestionLeafGroupOrderSerializer, name='QuestionLeafGroupOrderInputType')
QuestionOrderInputType = convert_serializer_to_type(QuestionOrderSerializer, name='QuestionOrderInputType')


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
    @sync_to_async
    def bulk_update_questionnair_question_groups_leaf_order(
        self,
        questionnaire_id: strawberry.ID,
        data: list[QuestionLeafGroupOrderInputType],
        info: Info,
    ) -> BulkBasicMutationResponseType[QuestionLeafGroupType]:
        if errors := ModelMutation.check_permissions(info, Project.Permission.UPDATE_QUESTION_GROUP):
            return BulkBasicMutationResponseType(errors=[errors])
        _data = {
            int(d['id']): d['order']
            for d in process_input_data(data)
        }
        queryset = QuestionLeafGroupType.get_queryset(None, None, info).filter(
            questionnaire=questionnaire_id,
            pk__in=_data.keys(),
        )
        to_update = []
        for obj in queryset:
            obj.order = _data[obj.id]
            to_update.append(obj)
        QuestionLeafGroup.objects.bulk_update(to_update, ('order',))
        return BulkBasicMutationResponseType(results=[i for i in queryset])

    @strawberry.mutation
    @sync_to_async
    def update_question_groups_leaf_visibility(
        self,
        questionnaire_id: strawberry.ID,
        ids: list[strawberry.ID],
        visibility: VisibilityActionEnum,
        info: Info,
    ) -> BulkBasicMutationResponseType[QuestionLeafGroupType]:
        if errors := ModelMutation.check_permissions(info, Project.Permission.UPDATE_QUESTION_GROUP):
            return BulkBasicMutationResponseType(errors=[errors])
        queryset = QuestionLeafGroupType.get_queryset(None, None, info).filter(
            questionnaire=questionnaire_id,
            id__in=ids,
        )
        is_hidden = visibility == VisibilityActionEnum.HIDE
        queryset.update(is_hidden=is_hidden)
        return BulkBasicMutationResponseType(results=[i for i in queryset])

    @strawberry.mutation
    @sync_to_async
    def bulk_update_questions_order(
        self,
        questionnaire_id: strawberry.ID,
        leaf_group_id: strawberry.ID,
        data: list[QuestionOrderInputType],
        info: Info,
    ) -> BulkBasicMutationResponseType[QuestionType]:
        if errors := ModelMutation.check_permissions(info, Project.Permission.UPDATE_QUESTION_GROUP):
            return BulkBasicMutationResponseType(errors=[errors])
        _data = {
            int(d['id']): d['order']
            for d in process_input_data(data)
        }
        queryset = QuestionType.get_queryset(None, None, info).filter(
            questionnaire=questionnaire_id,
            leaf_group=leaf_group_id,
            pk__in=_data.keys(),
        )
        to_update = []
        for obj in queryset:
            obj.order = _data[obj.id]
            to_update.append(obj)
        Question.objects.bulk_update(to_update, ('order',))
        return BulkBasicMutationResponseType(results=[i for i in queryset])

    @strawberry.mutation
    @sync_to_async
    def update_questions_visibility(
        self,
        questionnaire_id: strawberry.ID,
        ids: list[strawberry.ID],
        visibility: VisibilityActionEnum,
        info: Info,
    ) -> BulkBasicMutationResponseType[QuestionType]:
        if errors := ModelMutation.check_permissions(info, Project.Permission.UPDATE_QUESTION):
            return BulkBasicMutationResponseType(errors=[errors])
        queryset = QuestionType.get_queryset(None, None, info).filter(
            questionnaire=questionnaire_id,
            id__in=ids,
        )
        is_hidden = visibility == VisibilityActionEnum.HIDE
        queryset.update(is_hidden=is_hidden)
        return BulkBasicMutationResponseType(results=[i for i in queryset])

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
