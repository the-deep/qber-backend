import strawberry
from enum import Enum, auto

from utils.strawberry.enums import get_enum_name_from_django_field

from .models import Question, QuestionLeafGroup


QuestionTypeEnum = strawberry.enum(Question.Type, name='QuestionTypeEnum')
QuestionLeafGroupTypeEnum = strawberry.enum(QuestionLeafGroup.Type, name='QuestionLeafGroupTypeEnum')
QuestionLeafGroupCategory1TypeEnum = strawberry.enum(QuestionLeafGroup.Category1, name='QuestionLeafGroupCategory1TypeEnum')
QuestionLeafGroupCategory2TypeEnum = strawberry.enum(QuestionLeafGroup.Category2, name='QuestionLeafGroupCategory2TypeEnum')
QuestionLeafGroupCategory3TypeEnum = strawberry.enum(QuestionLeafGroup.Category3, name='QuestionLeafGroupCategory3TypeEnum')
QuestionLeafGroupCategory4TypeEnum = strawberry.enum(QuestionLeafGroup.Category4, name='QuestionLeafGroupCategory4TypeEnum')


enum_map = {
    get_enum_name_from_django_field(field): enum
    for field, enum in (
        (Question.type, QuestionTypeEnum),
        # QuestionLeafGroup
        (QuestionLeafGroup.type, QuestionLeafGroupTypeEnum),
        (QuestionLeafGroup.category_1, QuestionLeafGroupCategory1TypeEnum),
        (QuestionLeafGroup.category_2, QuestionLeafGroupCategory2TypeEnum),
        (QuestionLeafGroup.category_3, QuestionLeafGroupCategory3TypeEnum),
        (QuestionLeafGroup.category_4, QuestionLeafGroupCategory4TypeEnum),
    )
}


@strawberry.enum
class QuestionLeafGroupVisibilityActionEnum(Enum):
    SHOW = auto(), 'Show'
    HIDE = auto(), 'Hide'
