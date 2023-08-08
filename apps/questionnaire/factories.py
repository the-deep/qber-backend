import factory
from factory.django import DjangoModelFactory

from .models import Questionnaire, Question


class QuestionnaireFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'Questionnaire-{n}')

    class Meta:
        model = Questionnaire


class QuestionFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f'Question-{n}')

    class Meta:
        model = Question
