from asgiref.sync import sync_to_async
from strawberry.dataloader import DataLoader

from django.db import models
from django.utils.functional import cached_property

from apps.questionnaire.models import Question
from apps.questionnaire.types import QuestionCount


def total_questions_by_questionnare(keys: list[str]) -> list[QuestionCount]:
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


def total_questions_by_leaf_group(keys: list[str]) -> list[QuestionCount]:
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


class QuestionnaireDataLoader():
    @cached_property
    def total_questions_by_questionnare(self) -> list[QuestionCount]:
        return DataLoader(load_fn=sync_to_async(total_questions_by_questionnare))

    @cached_property
    def total_questions_by_leaf_group(self) -> list[QuestionCount]:
        return DataLoader(load_fn=sync_to_async(total_questions_by_leaf_group))
