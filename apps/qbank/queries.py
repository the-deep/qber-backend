import strawberry
import strawberry_django

from strawberry.types import Info

from utils.strawberry.paginations import CountList, pagination_field

from .filters import QuestionBankFilter, QBQuestionFilter
from .orders import QuestionBankOrder, QBQuestionOrder
from .types import QuestionBankType, QBQuestionType


@strawberry.type
class PrivateQuery:
    question_banks: CountList[QuestionBankType] = pagination_field(
        pagination=True,
        filters=QuestionBankFilter,
        order=QuestionBankOrder,
    )

    qb_questions: CountList[QBQuestionType] = pagination_field(
        pagination=True,
        filters=QBQuestionFilter,
        order=QBQuestionOrder,
    )

    @strawberry_django.field
    async def question_bank(self, info: Info, pk: strawberry.ID) -> QuestionBankType | None:
        return await QuestionBankType.get_queryset(None, None, info)\
            .filter(pk=pk)\
            .afirst()
