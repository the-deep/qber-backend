import strawberry
import strawberry_django

from strawberry.types import Info

from utils.strawberry.paginations import CountList, pagination_field

from .filters import QuestionnaireFilter, QuestionFilter
from .types import (
    QuestionnaireType,
    QuestionnaireOrder,
    QuestionType,
    QuestionOrder,
)


@strawberry.type
class PrivateProjectQuery:
    questionnaires: CountList[QuestionnaireType] = pagination_field(
        pagination=True,
        filters=QuestionnaireFilter,
        order=QuestionnaireOrder,
    )

    questions: CountList[QuestionType] = pagination_field(
        pagination=True,
        filters=QuestionFilter,
        order=QuestionOrder,
    )

    @strawberry_django.field
    async def questionnaire(self, info: Info, pk: strawberry.ID) -> QuestionnaireType | None:
        return await QuestionnaireType.get_queryset(None, None, info)\
            .filter(pk=pk)\
            .afirst()

    @strawberry_django.field
    async def question(self, info: Info, pk: strawberry.ID) -> QuestionType | None:
        return await QuestionType.get_queryset(None, None, info)\
            .filter(pk=pk)\
            .afirst()
