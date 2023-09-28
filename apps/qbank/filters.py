import strawberry
import strawberry_django

from .models import QuestionBank, QBQuestion
from .enums import (
    QberPriorityLevelTypeEnum,
    QberEnumeratorSkillTypeEnum,
    QberDataCollectionMethodTypeEnum,
)


class QberMetaQuestionFilterMixin:
    # QberMeta
    priority_levels: list[QberPriorityLevelTypeEnum]
    enumerator_skills: list[QberEnumeratorSkillTypeEnum]
    data_collection_methods: list[QberDataCollectionMethodTypeEnum]

    def filter_priority_levels(self, queryset):
        if self.priority_levels:
            queryset = queryset.filter(priority_level__in=self.priority_levels)
        return queryset

    def filter_enumerator_skills(self, queryset):
        if self.enumerator_skills:
            queryset = queryset.filter(enumerator_skill__in=self.enumerator_skills)
        return queryset

    def filter_data_collection_methods(self, queryset):
        if self.data_collection_methods:
            queryset = queryset.filter(data_collection_method__in=self.data_collection_methods)
        return queryset


@strawberry_django.filters.filter(QuestionBank, lookups=True)
class QuestionBankFilter:
    id: strawberry.auto
    title: strawberry.auto


@strawberry_django.filters.filter(QBQuestion, lookups=True)
class QBQuestionFilter(QberMetaQuestionFilterMixin):
    id: strawberry.auto
    qbank: strawberry.auto
    leaf_group: strawberry.auto
