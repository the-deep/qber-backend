import strawberry
import strawberry_django

from .models import (
    Questionnaire,
    Question,
    QuestionGroup,
    ChoiceCollection,
)


@strawberry_django.filters.filter(Questionnaire, lookups=True)
class QuestionnaireFilter:
    id: strawberry.auto
    project: strawberry.auto
    title: strawberry.auto


@strawberry_django.filters.filter(QuestionGroup, lookups=True)
class QuestionGroupFilter:
    id: strawberry.auto
    questionnaire: strawberry.auto
    name: strawberry.auto
    label: strawberry.auto


@strawberry_django.filters.filter(ChoiceCollection, lookups=True)
class QuestionChoiceCollectionFilter:
    id: strawberry.auto
    questionnaire: strawberry.auto
    name: strawberry.auto
    label: strawberry.auto


@strawberry_django.filters.filter(Question, lookups=True)
class QuestionFilter:
    id: strawberry.auto
    questionnaire: strawberry.auto
    name: strawberry.auto
    label: strawberry.auto
