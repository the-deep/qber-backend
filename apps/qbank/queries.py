import strawberry
import strawberry_django
from asgiref.sync import sync_to_async

from strawberry.types import Info

from utils.strawberry.paginations import CountList, pagination_field

from .models import QuestionBank
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

    @strawberry_django.field
    @sync_to_async
    def active_question_bank(self) -> QuestionBankType | None:
        return QuestionBank.get_active()
