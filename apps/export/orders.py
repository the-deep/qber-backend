import strawberry
import strawberry_django

from .models import QuestionnaireExport


@strawberry_django.ordering.order(QuestionnaireExport)
class QuestionnaireExportOrder:
    id: strawberry.auto
    exported_at: strawberry.auto
