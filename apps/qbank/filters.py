import strawberry
import strawberry_django

from .models import QuestionBank, QBQuestion


@strawberry_django.filters.filter(QuestionBank, lookups=True)
class QuestionBankFilter:
    id: strawberry.auto
    title: strawberry.auto


@strawberry_django.filters.filter(QBQuestion, lookups=True)
class QBQuestionFilter:
    id: strawberry.auto
    qbank: strawberry.auto
    leaf_group: strawberry.auto
