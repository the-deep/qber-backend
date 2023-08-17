import strawberry
import strawberry_django

from .models import (
    Questionnaire,
    Question,
    QuestionGroup,
    ChoiceCollection,
)


@strawberry_django.ordering.order(Questionnaire)
class QuestionnaireOrder:
    id: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.ordering.order(QuestionGroup)
class QuestionGroupOrder:
    id: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.ordering.order(ChoiceCollection)
class QuestionChoiceCollectionOrder:
    id: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.ordering.order(Question)
class QuestionOrder:
    id: strawberry.auto
    created_at: strawberry.auto