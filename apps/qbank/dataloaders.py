from asgiref.sync import sync_to_async
from strawberry.dataloader import DataLoader

from django.db import models
from django.utils.functional import cached_property

from apps.qbank.models import QBQuestion


def total_questions_by_qbank(keys: list[str]) -> list[int]:
    qs = (
        QBQuestion.objects
        .filter(qbank__in=keys)
        .order_by()
        .values('qbank')
        .annotate(
            count=models.Count('id'),
        ).values_list('qbank', 'count')
    )
    _map = {
        qbank_id: count
        for qbank_id, count in qs
    }
    return [_map.get(key, 0) for key in keys]


def total_questions_by_leaf_group(keys: list[str]) -> list[int]:
    qs = (
        QBQuestion.objects
        .filter(leaf_group__in=keys)
        .order_by()
        .values('leaf_group')
        .annotate(
            count=models.Count('id'),
        ).values_list('leaf_group', 'count')
    )
    _map = {
        leaf_group_id: count
        for leaf_group_id, count in qs
    }
    return [_map.get(key, 0) for key in keys]


class QBankDataLoader():
    @cached_property
    def total_questions_by_qbank(self) -> list[int]:
        return DataLoader(load_fn=sync_to_async(total_questions_by_qbank))

    @cached_property
    def total_questions_by_leaf_group(self) -> list[int]:
        return DataLoader(load_fn=sync_to_async(total_questions_by_leaf_group))
