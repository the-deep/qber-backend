import strawberry

from utils.strawberry.enums import get_enum_name_from_django_field

from .base_models import QberMetaData
from .models import (
    QBQuestion,
    QBLeafGroup,
)


# Questionnaire
QberPriorityLevelTypeEnum = strawberry.enum(QberMetaData.PriorityLevel, name='QberMetaDataPriorityLevelTypeEnum')
QberEnumeratorSkillTypeEnum = strawberry.enum(QberMetaData.EnumeratorSkill, name='QberEnumeratorSkillTypeEnum')
QberDataCollectionMethodTypeEnum = strawberry.enum(
    QberMetaData.DataCollectionMethod, name='QberDataCollectionMethodTypeEnum')

# Question
QuestionTypeEnum = strawberry.enum(QBQuestion.Type, name='QberQuestionTypeEnum')

# QuestionLeafGroup
QuestionLeafGroupTypeEnum = strawberry.enum(QBLeafGroup.Type, name='QuestionLeafGroupTypeEnum')
QuestionLeafGroupCategory1TypeEnum = strawberry.enum(QBLeafGroup.Category1, name='QuestionLeafGroupCategory1TypeEnum')
QuestionLeafGroupCategory2TypeEnum = strawberry.enum(QBLeafGroup.Category2, name='QuestionLeafGroupCategory2TypeEnum')
QuestionLeafGroupCategory3TypeEnum = strawberry.enum(QBLeafGroup.Category3, name='QuestionLeafGroupCategory3TypeEnum')
QuestionLeafGroupCategory4TypeEnum = strawberry.enum(QBLeafGroup.Category4, name='QuestionLeafGroupCategory4TypeEnum')


enum_map = {
    get_enum_name_from_django_field(field): enum
    for field, enum in (
        # Question
        (QBQuestion.type, QuestionTypeEnum),
        (QBQuestion.priority_level, QberPriorityLevelTypeEnum),
        (QBQuestion.enumerator_skill, QberEnumeratorSkillTypeEnum),
        (QBQuestion.data_collection_method, QberDataCollectionMethodTypeEnum),
        # QuestionLeafGroup
        (QBLeafGroup.type, QuestionLeafGroupTypeEnum),
        (QBLeafGroup.category_1, QuestionLeafGroupCategory1TypeEnum),
        (QBLeafGroup.category_2, QuestionLeafGroupCategory2TypeEnum),
        (QBLeafGroup.category_3, QuestionLeafGroupCategory3TypeEnum),
        (QBLeafGroup.category_4, QuestionLeafGroupCategory4TypeEnum),
    )
}
