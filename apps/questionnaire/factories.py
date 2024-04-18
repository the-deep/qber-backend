import factory
from factory.django import DjangoModelFactory

from apps.qbank.factories import QBLeafGroupFactory, QBQuestionFactory
from .models import (
    Questionnaire,
    Question,
    Choice,
    ChoiceCollection,
    QuestionLeafGroup,
)


class QuestionnaireFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'Questionnaire-{n}')

    class Meta:
        model = Questionnaire


class QuestionLeafGroupFactory(QBLeafGroupFactory):
    name = factory.Sequence(lambda n: f'Question-Group-{n}')

    class Meta:
        model = QuestionLeafGroup


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


class QuestionFactory(QBQuestionFactory):
    name = factory.Sequence(lambda n: f'Question-{n}')

    class Meta:
        model = Question

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        obj.questionnaire = obj.leaf_group.questionnaire
        if getattr(obj, 'choice_collection', None):
            assert obj.choice_collection.questionnaire == obj.questionnaire
        obj.save()
        return obj
