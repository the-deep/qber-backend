import strawberry
import strawberry_django

from strawberry.types import Info

from utils.strawberry.paginations import CountList, pagination_field

from .types import QuestionnaireExportType
from .filters import QuestionnaireExportFilter
from .orders import QuestionnaireExportOrder


@strawberry.type
class PrivateProjectQuery:
    questionnaire_exports: CountList[QuestionnaireExportType] = pagination_field(
        pagination=True,
        filters=QuestionnaireExportFilter,
        order=QuestionnaireExportOrder,
    )

    @strawberry_django.field
    async def questionnaire_export(self, info: Info, pk: strawberry.ID) -> QuestionnaireExportType | None:
        return await QuestionnaireExportType.get_queryset(None, None, info)\
            .filter(pk=pk)\
            .afirst()
