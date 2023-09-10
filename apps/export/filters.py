import strawberry
import strawberry_django

from .enums import (
    QuestionnaireExportTypeEnum,
    QuestionnaireExportStatusEnum,
)
from .models import QuestionnaireExport


@strawberry_django.filters.filter(QuestionnaireExport, lookups=True)
class QuestionnaireExportFilter:
    id: strawberry.auto
    questionnaire: strawberry.auto
    exported_at: strawberry.auto
    type: QuestionnaireExportTypeEnum
    status: QuestionnaireExportStatusEnum
