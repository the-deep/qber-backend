import strawberry
from enum import Enum, auto

from utils.strawberry.enums import get_enum_name_from_django_field

from .models import (
    Question,
    Questionnaire,
    QuestionLeafGroup,
)


# Questionnaire
QuestionnairePriorityLevelTypeEnum = strawberry.enum(
    Questionnaire.PriorityLevel, name='QuestionnairePriorityLevelTypeEnum')
QuestionnaireEnumeratorSkillTypeEnum = strawberry.enum(
    Questionnaire.EnumeratorSkill, name='QuestionnaireEnumeratorSkillTypeEnum')
QuestionnaireDataCollectionMethodTypeEnum = strawberry.enum(
    Questionnaire.DataCollectionMethod, name='QuestionnaireDataCollectionMethodTypeEnum')

# Question
QuestionTypeEnum = strawberry.enum(Question.Type, name='QuestionTypeEnum')

# QuestionLeafGroup
QuestionLeafGroupTypeEnum = strawberry.enum(QuestionLeafGroup.Type, name='QuestionLeafGroupTypeEnum')
QuestionLeafGroupCategory1TypeEnum = strawberry.enum(QuestionLeafGroup.Category1, name='QuestionLeafGroupCategory1TypeEnum')
QuestionLeafGroupCategory2TypeEnum = strawberry.enum(QuestionLeafGroup.Category2, name='QuestionLeafGroupCategory2TypeEnum')
QuestionLeafGroupCategory3TypeEnum = strawberry.enum(QuestionLeafGroup.Category3, name='QuestionLeafGroupCategory3TypeEnum')
QuestionLeafGroupCategory4TypeEnum = strawberry.enum(QuestionLeafGroup.Category4, name='QuestionLeafGroupCategory4TypeEnum')


enum_map = {
    get_enum_name_from_django_field(field): enum
    for field, enum in (
        # Questionnaire
        (Questionnaire.priority_level, QuestionnairePriorityLevelTypeEnum),
        (Questionnaire.enumerator_skill, QuestionnaireEnumeratorSkillTypeEnum),
        (Questionnaire.data_collection_method, QuestionnaireDataCollectionMethodTypeEnum),
        # Question
        (Question.type, QuestionTypeEnum),
        (Question.priority_level, QuestionnairePriorityLevelTypeEnum),
        (Question.enumerator_skill, QuestionnaireEnumeratorSkillTypeEnum),
        (Question.data_collection_method, QuestionnaireDataCollectionMethodTypeEnum),
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
