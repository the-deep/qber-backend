import strawberry
import strawberry_django

from strawberry.types import Info

from utils.strawberry.paginations import CountList, pagination_field

from .filters import (
    QuestionnaireFilter,
    QuestionFilter,
    QuestionLeafGroupFilter,
    QuestionChoiceCollectionFilter,
)
from .orders import (
    QuestionnaireOrder,
    QuestionOrder,
    QuestionLeafGroupOrder,
    QuestionChoiceCollectionOrder,
)
from .types import (
    QuestionnaireType,
    QuestionLeafGroupType,
    QuestionType,
    QuestionChoiceCollectionType,
)


@strawberry.type
class PrivateProjectQuery:
    questionnaires: CountList[QuestionnaireType] = pagination_field(
        pagination=True,
        filters=QuestionnaireFilter,
        order=QuestionnaireOrder,
    )

    leafGroups: CountList[QuestionLeafGroupType] = pagination_field(
        pagination=True,
        filters=QuestionLeafGroupFilter,
        order=QuestionLeafGroupOrder,
    )

    choice_collections: CountList[QuestionChoiceCollectionType] = pagination_field(
        pagination=True,
        filters=QuestionChoiceCollectionFilter,
        order=QuestionChoiceCollectionOrder,
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
    async def leaf_group(self, info: Info, pk: strawberry.ID) -> QuestionLeafGroupType | None:
        return await QuestionLeafGroupType.get_queryset(None, None, info)\
            .filter(pk=pk)\
            .afirst()

    @strawberry_django.field
    async def choice_collection(self, info: Info, pk: strawberry.ID) -> QuestionChoiceCollectionType | None:
        return await QuestionChoiceCollectionType.get_queryset(None, None, info)\
            .filter(pk=pk)\
            .afirst()

    @strawberry_django.field
    async def question(self, info: Info, pk: strawberry.ID) -> QuestionType | None:
        return await QuestionType.get_queryset(None, None, info)\
            .filter(pk=pk)\
            .afirst()
