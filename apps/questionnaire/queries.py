import strawberry
import strawberry_django

from strawberry.types import Info

from utils.strawberry.paginations import CountList, pagination_field

from .filters import QuestionnaireFilter
from .types import QuestionnaireType


@strawberry.type
class PrivateProjectQuery:
    questionnaires: CountList[QuestionnaireType] = pagination_field(
        pagination=True,
        filters=QuestionnaireFilter,
    )

    @strawberry_django.field
    async def questionnaire(self, info: Info, pk: strawberry.ID) -> QuestionnaireType | None:
        return await QuestionnaireType.get_queryset(None, None, info)\
            .filter(pk=pk)\
            .afirst()
