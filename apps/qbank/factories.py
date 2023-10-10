import factory
import functools
import random
from factory.django import DjangoModelFactory

from .models import (
    QuestionBank,
    QBQuestion,
    QBChoice,
    QBChoiceCollection,
    QBLeafGroup,
)


class QuestionBankFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'QuestionBank-{n}')

    class Meta:
        model = QuestionBank


class QBLeafGroupFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f'QB-Leaf-Group-{n}')

    class Meta:
        model = QBLeafGroup

    @staticmethod
    def random_category_generator(count):
        categories = []
        _count = 0
        max_iter = 500
        while True:
            _type = random.choice(list(QBLeafGroup.TYPE_CATEGORY_MAP.keys()))
            category1, category2, category3, category4 = [None] * 4
            if _type == QBLeafGroup.Type.MATRIX_1D:
                # Category 1
                category1_choices = list(QBLeafGroup.TYPE_CATEGORY_MAP[_type].keys())
                category1 = random.choice(category1_choices)
                # Category 2
                category2_choices = list(QBLeafGroup.TYPE_CATEGORY_MAP[_type][category1])
                category2 = random.choice(category2_choices)
            elif _type == QBLeafGroup.Type.MATRIX_2D:
                # Rows
                # -- Category 1
                category1_choices = list(QBLeafGroup.TYPE_CATEGORY_MAP[_type]['rows'].keys())
                category1 = random.choice(category1_choices)
                # -- Category 2
                category2_choices = list(QBLeafGroup.TYPE_CATEGORY_MAP[_type]['rows'][category1])
                category2 = random.choice(category2_choices)
                # Columns
                # -- Category 3
                category3_choices = list(QBLeafGroup.TYPE_CATEGORY_MAP[_type]['columns'].keys())
                category3 = random.choice(category3_choices)
                # -- Category 4
                category4_choices = list(QBLeafGroup.TYPE_CATEGORY_MAP[_type]['columns'][category3])
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
        matrix_1d = QBLeafGroup.Type.MATRIX_1D
        matrix_2d = QBLeafGroup.Type.MATRIX_2D
        return {
            matrix_1d: [
                {
                    'type': matrix_1d,
                    'category_1': category_1,
                    'category_2': category_2,
                }
                for category_1, categories_2 in QBLeafGroup.TYPE_CATEGORY_MAP[matrix_1d].items()
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
                for category_1, categories_2 in QBLeafGroup.TYPE_CATEGORY_MAP[matrix_2d]['rows'].items()
                for category_2 in categories_2
                for category_3, categories_4 in QBLeafGroup.TYPE_CATEGORY_MAP[matrix_2d]['columns'].items()
                for category_4 in categories_4
                if len(categories_4) > 0  # TODO: Support for empty category_4
            ],
        }

    @classmethod
    def static_generator(cls, count, **kwargs):
        _type = kwargs.get('type', QBLeafGroup.Type.MATRIX_1D)
        collections = cls.get_static_category_collections()[_type]
        if len(collections) < count:
            raise Exception('Provided count is higher then available iteration')
        leaf_groups = []
        order = 1
        for group_data in collections[:count]:
            leaf_groups.append(
                cls(
                    type=group_data['type'],
                    category_1=group_data['category_1'],
                    category_2=group_data['category_2'],
                    category_3=group_data.get('category_3'),
                    category_4=group_data.get('category_4'),
                    order=order,
                    **kwargs,
                )
            )
            order += 1
        return leaf_groups


class QBChoiceFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f'QBChoice-{n}')
    label = factory.Sequence(lambda n: f'QBChoice-{n}')

    class Meta:
        model = QBChoice


class QBChoiceCollectionFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f'QBChoice-Collection-{n}')
    label = factory.Sequence(lambda n: f'QBChoice-Collection-{n}')

    class Meta:
        model = QBChoiceCollection


class QBQuestionFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f'QBQuestion-{n}')
    label = factory.Faker('text')
    type = QBQuestion.Type.INTEGER

    class Meta:
        model = QBQuestion

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        obj.qbank = obj.leaf_group.qbank
        if getattr(obj, 'choice_collection', None):
            assert obj.choice_collection.qbank == obj.qbank
        obj.save()
        return obj
