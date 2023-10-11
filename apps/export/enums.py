import strawberry

from utils.strawberry.enums import get_enum_name_from_django_field

from .models import QuestionnaireExport


# Questionnaire
QuestionnaireExportStatusEnum = strawberry.enum(QuestionnaireExport.Status, name='QuestionnaireExportStatusEnum')


enum_map = {
    get_enum_name_from_django_field(field): enum
    for field, enum in (
        (QuestionnaireExport.status, QuestionnaireExportStatusEnum),
    )
}
