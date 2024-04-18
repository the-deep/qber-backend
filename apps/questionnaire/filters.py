import strawberry
import strawberry_django

from apps.qbank.filters import QberMetaQuestionFilterMixin
from .enums import (
    QuestionTypeEnum,
)
from .models import (
    Questionnaire,
    Question,
    ChoiceCollection,
)


@strawberry_django.filters.filter(Questionnaire, lookups=True)
class QuestionnaireFilter:
    id: strawberry.auto
    project: strawberry.auto
    title: strawberry.auto


@strawberry_django.filters.filter(ChoiceCollection, lookups=True)
class QuestionChoiceCollectionFilter:
    id: strawberry.auto
    questionnaire: strawberry.auto
    name: strawberry.auto
    label: strawberry.auto


@strawberry_django.filters.filter(Question, lookups=True)
class QuestionFilter(QberMetaQuestionFilterMixin):
    id: strawberry.auto
    questionnaire: strawberry.auto
    choice_collection: strawberry.auto
    type: QuestionTypeEnum
    name: strawberry.auto
    label: strawberry.auto
    leaf_group: strawberry.auto
    is_hidden: strawberry.auto
