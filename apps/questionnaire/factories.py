import factory
from factory.django import DjangoModelFactory

from .models import (
    Questionnaire,
    Question,
    Choice,
    ChoiceCollection,
    QuestionGroup,
)


class QuestionnaireFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'Questionnaire-{n}')

    class Meta:
        model = Questionnaire


class QuestionGroupFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f'Question-Group-{n}')
    label = factory.Sequence(lambda n: f'Question-Group-{n}')

    class Meta:
        model = QuestionGroup


class ChoiceFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f'Choice-{n}')
    label = factory.Sequence(lambda n: f'Choice-{n}')

    class Meta:
        model = Choice


class ChoiceCollectionFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f'Choice-Collection-{n}')
    label = factory.Sequence(lambda n: f'Choice-Collection-{n}')

    class Meta:
        model = ChoiceCollection


class QuestionFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f'Question-{n}')
    label = factory.Sequence(lambda n: f'Question-{n}')

    class Meta:
        model = Question
