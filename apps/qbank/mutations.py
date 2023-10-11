import strawberry
from asgiref.sync import sync_to_async
from strawberry.types import Info
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from utils.strawberry.mutations import (
    MutationResponseType,
    mutation_is_not_valid,
)
from utils.strawberry.transformers import convert_serializer_to_type
from utils.strawberry.mutations import process_input_data, generate_error_message

from apps.common.models import GlobalPermission
from .serializers import CreateQuestionBankSerializer
from .types import (
    QuestionBankType,
)

CreateQuestionBankInput = convert_serializer_to_type(CreateQuestionBankSerializer, name='CreateQuestionBankInput')


@strawberry.type
class PrivateMutation:

    @strawberry.mutation
    @sync_to_async
    def create_question_bank(
        self,
        data: CreateQuestionBankInput,
        info: Info,
    ) -> MutationResponseType[QuestionBankType]:
        if error := info.context.has_global_perm(GlobalPermission.Type.UPLOAD_QBANK):
            return MutationResponseType(
                ok=False,
                errors=generate_error_message(error),
            )
        serializer = CreateQuestionBankSerializer(
            data=process_input_data(data),
            context={'request': info.context.request},
        )
        if errors := mutation_is_not_valid(serializer):
            return MutationResponseType(
                ok=False,
                errors=errors,
            )
        instance = serializer.save()
        return MutationResponseType(
            result=instance,
        )

    @strawberry.mutation
    @sync_to_async
    def activate_question_bank(
        self,
        id: strawberry.ID,
        info: Info,
    ) -> MutationResponseType[QuestionBankType]:
        if error := info.context.has_global_perm(GlobalPermission.Type.ACTIVATE_QBANK):
            return MutationResponseType(
                ok=False,
                errors=generate_error_message(error),
            )
        queryset = QuestionBankType.get_queryset(None, None, info)
        qbank = get_object_or_404(queryset, id=id)
        try:
            qbank.activate()
        except ValidationError as e:
            return MutationResponseType(
                ok=False,
                errors=generate_error_message(str(e)),
            )
        return MutationResponseType(
            result=qbank,
            ok=True,
        )
