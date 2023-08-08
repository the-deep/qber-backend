import strawberry

from utils.strawberry.enums import get_enum_name_from_django_field

from .models import Question


QuestionTypeEnum = strawberry.enum(Question.Type, name='QuestionTypeEnum')


enum_map = {
    get_enum_name_from_django_field(field): enum
    for field, enum in (
        (Question.type, QuestionTypeEnum),
    )
}
