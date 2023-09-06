import factory
import functools
import random
from factory.django import DjangoModelFactory

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


class QuestionLeafGroupFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f'Question-Group-{n}')

    class Meta:
        model = QuestionLeafGroup

    @staticmethod
    def random_category_generator(count):
        categories = []
        _count = 0
        max_iter = 500
        while True:
            _type = random.choice(list(QuestionLeafGroup.TYPE_CATEGORY_MAP.keys()))
            category1, category2, category3, category4 = [None] * 4
            if _type == QuestionLeafGroup.Type.MATRIX_1D:
                # Category 1
                category1_choices = list(QuestionLeafGroup.TYPE_CATEGORY_MAP[_type].keys())
                category1 = random.choice(category1_choices)
                # Category 2
                category2_choices = list(QuestionLeafGroup.TYPE_CATEGORY_MAP[_type][category1])
                category2 = random.choice(category2_choices)
            elif _type == QuestionLeafGroup.Type.MATRIX_2D:
                # Rows
                # -- Category 1
                category1_choices = list(QuestionLeafGroup.TYPE_CATEGORY_MAP[_type]['rows'].keys())
                category1 = random.choice(category1_choices)
                # -- Category 2
                category2_choices = list(QuestionLeafGroup.TYPE_CATEGORY_MAP[_type]['rows'][category1])
                category2 = random.choice(category2_choices)
                # Columns
                # -- Category 3
                category3_choices = list(QuestionLeafGroup.TYPE_CATEGORY_MAP[_type]['columns'].keys())
                category3 = random.choice(category3_choices)
                # -- Category 4
                category4_choices = list(QuestionLeafGroup.TYPE_CATEGORY_MAP[_type]['columns'][category3])
                if not category4_choices:
                    continue
                if len(category4_choices) == 1:
                    category4 = category4_choices[0]
                else:
                    category4 = random.choice(category4_choices)
            categories.append((_type, category1, category2, category3, category4))
            _count += 1
            if count > max_iter or _count > count:
                break
        return set(categories)

    @staticmethod
    @functools.lru_cache
    def get_static_category_collections() -> dict:
        matrix_1d = QuestionLeafGroup.Type.MATRIX_1D
        matrix_2d = QuestionLeafGroup.Type.MATRIX_2D
        return {
            matrix_1d: [
                {
                    'type': matrix_1d,
                    'category_1': category_1,
                    'category_2': category_2,
                }
                for category_1, categories_2 in QuestionLeafGroup.TYPE_CATEGORY_MAP[matrix_1d].items()
                for category_2 in categories_2
            ],
            matrix_2d: [
                {
                    'type': matrix_1d,
                    'category_1': category_1,
                    'category_2': category_2,
                    'category_3': category_3,
                    'category_4': category_4,
                }
                for category_1, categories_2 in QuestionLeafGroup.TYPE_CATEGORY_MAP[matrix_2d]['rows'].items()
                for category_2 in categories_2
                for category_3, categories_4 in QuestionLeafGroup.TYPE_CATEGORY_MAP[matrix_2d]['columns'].items()
                for category_4 in categories_4
                if len(categories_4) > 0  # TODO: Support for empty category_4
            ],
        }

    @classmethod
    def static_generator(cls, count, **kwargs):
        _type = kwargs.get('type', QuestionLeafGroup.Type.MATRIX_1D)
        collections = cls.get_static_category_collections()[_type]
        if len(collections) < count:
            raise Exception('Provided count is higher then avaiable iteration')
        leaf_groups = []
        for group_data in collections[:count]:
            leaf_groups.append(
                QuestionLeafGroupFactory(
                    type=group_data['type'],
                    category_1=group_data['category_1'],
                    category_2=group_data['category_2'],
                    category_3=group_data.get('category_3'),
                    category_4=group_data.get('category_4'),
                    **kwargs,
                )
            )
        return leaf_groups


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
    type = Question.Type.INTEGER

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
