import strawberry
import strawberry_django

from .enums import (
    QuestionTypeEnum,
    QuestionLeafGroupTypeEnum,
)
from .models import (
    Questionnaire,
    Question,
    QuestionLeafGroup,
    ChoiceCollection,
)


@strawberry_django.filters.filter(Questionnaire, lookups=True)
class QuestionnaireFilter:
    id: strawberry.auto
    project: strawberry.auto
    title: strawberry.auto


@strawberry_django.filters.filter(QuestionLeafGroup, lookups=True)
class QuestionLeafGroupFilter:
    id: strawberry.auto
    questionnaire: strawberry.auto
    name: strawberry.auto
    is_hidden: strawberry.auto
    type: QuestionLeafGroupTypeEnum


@strawberry_django.filters.filter(ChoiceCollection, lookups=True)
class QuestionChoiceCollectionFilter:
    id: strawberry.auto
    questionnaire: strawberry.auto
    name: strawberry.auto
    label: strawberry.auto


@strawberry_django.filters.filter(Question, lookups=True)
class QuestionFilter:
    id: strawberry.auto
    questionnaire: strawberry.auto
    choice_collection: strawberry.auto
    type: QuestionTypeEnum
    name: strawberry.auto
    label: strawberry.auto
    leaf_group: strawberry.auto
    include_child_group: bool | None = False

    def filter_leaf_group(self, queryset):
        # NOTE: logic is in filter_include_child_group
        return queryset

    def filter_include_child_group(self, queryset):
        if self.leaf_group is strawberry.UNSET:
            # Nothing to do here
            return queryset
        if not self.include_child_group:
            return queryset.filter(group=self.leaf_group.pk)
        all_groups = [
            self.leaf_group.pk,
            # TODO: *get_child_groups_id(self.leaf_group.pk),
        ]
        return queryset.filter(group__in=all_groups)
