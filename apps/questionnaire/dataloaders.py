from collections import defaultdict
from asgiref.sync import sync_to_async
from strawberry.dataloader import DataLoader

from django.db import models
from django.utils.functional import cached_property

from apps.qbank.models import QuestionBank
from apps.questionnaire.models import Question, Choice
from apps.questionnaire.types import QuestionCount


def total_questions_by_questionnaire(keys: list[int]) -> list[QuestionCount]:
    qs = (
        Question.objects
        .filter(questionnaire__in=keys)
        .order_by()
        .values('questionnaire')
        .annotate(
            count=models.Count('id'),
            visible_count=models.Count(
                'id',
                filter=models.Q(is_hidden=False) & models.Q(leaf_group__is_hidden=False)
            )
        ).values_list('questionnaire', 'count', 'visible_count')
    )
    _map = {
        questionnaire_id: QuestionCount(
            total=count,
            visible=visible,
        )
        for questionnaire_id, count, visible in qs
    }
    return [_map.get(key, QuestionCount()) for key in keys]


def total_questions_by_leaf_group(keys: list[int]) -> list[QuestionCount]:
    qs = (
        Question.objects
        .filter(leaf_group__in=keys)
        .order_by()
        .values('leaf_group')
        .annotate(
            count=models.Count('id'),
            visible_count=models.Count(
                'id',
                filter=models.Q(is_hidden=False) & models.Q(leaf_group__is_hidden=False)
            )
        ).values_list('leaf_group', 'count', 'visible_count')
    )
    _map = {
        leaf_group_id: QuestionCount(
            total=count,
            visible=visible,
        )
        for leaf_group_id, count, visible in qs
    }
    return [_map.get(key, QuestionCount()) for key in keys]


def load_qbank(keys: list[int]) -> list[QuestionBank]:
    qs = QuestionBank.objects.filter(id__in=keys)
    _map = {
        qbank.pk: qbank
        for qbank in qs
    }
    return [_map[key] for key in keys]


def load_choices(keys: list[int]) -> list[list[Choice]]:
    # Keys are of ChoiceCollections
    qs = Choice.objects.filter(collection__in=keys)
    _map = defaultdict(list)
    for qb_choice in qs.all():
        _map[qb_choice.collection_id].append(qb_choice)
    return [_map.get(key, []) for key in keys]


def total_required_duration_by_questionnaire(keys: list[int]) -> list[float]:
    qs = (
        Question.objects
        .filter(questionnaire__in=keys)
        .order_by().values('questionnaire')
        .annotate(
            total_required_duration=models.Sum(
                'required_duration',
                filter=models.Q(is_hidden=False) & models.Q(leaf_group__is_hidden=False)
            )
        )
    )
    _map = {
        questionnaire_id: (total_required_duration or 0)
        for questionnaire_id, total_required_duration in (
            qs.values_list('questionnaire', 'total_required_duration')
        )
    }
    return [_map.get(key, 0) for key in keys]


class QuestionnaireDataLoader():
    @cached_property
    def total_questions_by_questionnaire(self) -> list[QuestionCount]:
        return DataLoader(load_fn=sync_to_async(total_questions_by_questionnaire))

    @cached_property
    def total_questions_by_leaf_group(self) -> list[QuestionCount]:
        return DataLoader(load_fn=sync_to_async(total_questions_by_leaf_group))

    @cached_property
    def load_qbank(self) -> list[QuestionBank]:
        return DataLoader(load_fn=sync_to_async(load_qbank))

    @cached_property
    def load_choices(self) -> list[list[Choice]]:
        return DataLoader(load_fn=sync_to_async(load_choices))

    @cached_property
    def total_required_duration_by_questionnaire(self) -> list[float]:
        return DataLoader(load_fn=sync_to_async(total_required_duration_by_questionnaire))
