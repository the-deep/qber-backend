import strawberry
import strawberry_django

from .models import QuestionBank, QBQuestion


@strawberry_django.ordering.order(QuestionBank)
class QuestionBankOrder:
    id: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.ordering.order(QBQuestion)
class QBQuestionOrder:
    id: strawberry.auto
    created_at: strawberry.auto
