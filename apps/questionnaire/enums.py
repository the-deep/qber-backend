import strawberry
from enum import Enum, auto

from utils.strawberry.enums import get_enum_name_from_django_field

from apps.qbank.enums import (
    QberPriorityLevelTypeEnum,
    QberEnumeratorSkillTypeEnum,
    QberDataCollectionMethodTypeEnum,
    QuestionTypeEnum,
    QuestionLeafGroupTypeEnum,
    QuestionLeafGroupCategory1TypeEnum,
    QuestionLeafGroupCategory2TypeEnum,
    QuestionLeafGroupCategory3TypeEnum,
    QuestionLeafGroupCategory4TypeEnum,

)
from .models import (
    Question,
    Questionnaire,
    QuestionLeafGroup,
)


enum_map = {
    get_enum_name_from_django_field(field): enum
    for field, enum in (
        # Questionnaire
        (Questionnaire.priority_level, QberPriorityLevelTypeEnum),
        (Questionnaire.enumerator_skill, QberEnumeratorSkillTypeEnum),
        (Questionnaire.data_collection_method, QberDataCollectionMethodTypeEnum),
        # Question
        (Question.type, QuestionTypeEnum),
        (Question.priority_level, QberPriorityLevelTypeEnum),
        (Question.enumerator_skill, QberEnumeratorSkillTypeEnum),
        (Question.data_collection_method, QberDataCollectionMethodTypeEnum),
        # QuestionLeafGroup
        (QuestionLeafGroup.type, QuestionLeafGroupTypeEnum),
        (QuestionLeafGroup.category_1, QuestionLeafGroupCategory1TypeEnum),
        (QuestionLeafGroup.category_2, QuestionLeafGroupCategory2TypeEnum),
        (QuestionLeafGroup.category_3, QuestionLeafGroupCategory3TypeEnum),
        (QuestionLeafGroup.category_4, QuestionLeafGroupCategory4TypeEnum),
    )
}


@strawberry.enum
class VisibilityActionEnum(Enum):
    SHOW = auto(), 'Show'
    HIDE = auto(), 'Hide'
