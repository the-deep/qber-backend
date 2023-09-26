import typing
import strawberry
import strawberry_django
from strawberry.types import Info
from django.db import models

from utils.common import get_queryset_for_model
from utils.strawberry.enums import enum_display_field, enum_field
from apps.common.types import UserResourceTypeMixin

from .models import (
    QuestionBank,
    QBQuestion,
    QBLeafGroup,
    QBChoiceCollection,
    QBChoice,
)


@strawberry_django.type(QBLeafGroup)
class QBLeafGroupType:
    id: strawberry.ID
    name: strawberry.auto
    type = enum_field(QBLeafGroup.type)
    type_display = enum_display_field(QBLeafGroup.type)
    order: strawberry.auto
    # Categories
    # -- For Matrix1D/Matrix2D
    category_1 = enum_field(QBLeafGroup.category_1)
    category_1_display = enum_display_field(QBLeafGroup.category_1)
    category_2 = enum_field(QBLeafGroup.category_2)
    category_2_display = enum_display_field(QBLeafGroup.category_2)
    # -- For Matrix2D
    category_3 = enum_field(QBLeafGroup.category_3)
    category_3_display = enum_display_field(QBLeafGroup.category_3)
    category_4 = enum_field(QBLeafGroup.category_4)
    category_4_display = enum_display_field(QBLeafGroup.category_4)
    # Misc
    relevant: strawberry.auto

    @strawberry.field
    def qbank_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.qbank_id))

    @staticmethod
    def get_queryset(_, queryset: models.QuerySet | None, info: Info):
        return get_queryset_for_model(QBLeafGroup, queryset)

    @strawberry.field
    def total_questions(self, info: Info) -> int:
        return info.context.dl.qbank.total_questions_by_leaf_group.load(self.id)


@strawberry_django.type(QuestionBank)
class QuestionBankType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    is_active: strawberry.auto

    @staticmethod
    def get_queryset(_, queryset: models.QuerySet | None, info: Info):
        # TODO: Only show the latest
        return get_queryset_for_model(QuestionBank, queryset)

    @strawberry_django.field
    async def leaf_groups(self, info: Info) -> list[QBLeafGroupType]:
        queryset = QBLeafGroupType.get_queryset(None, None, info).filter(qbank=self.pk)
        return [q async for q in queryset]

    @strawberry_django.field
    async def choice_collections(self, info: Info) -> list['QBChoiceCollectionType']:
        queryset = QBChoiceCollectionType.get_queryset(None, None, info).filter(qbank=self.pk)
        return [q async for q in queryset]

    @strawberry.field
    def total_questions(self, info: Info) -> int:
        return info.context.dl.qbank.total_questions_by_qbank.load(self.id)


@strawberry_django.type(QBChoice)
class QBChoiceType:
    id: strawberry.ID
    name: strawberry.auto
    label: strawberry.auto
    # geometry: strawberry.auto

    @strawberry.field
    def collection_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.collection_id))


@strawberry_django.type(QBChoiceCollection)
class QBChoiceCollectionType:
    id: strawberry.ID
    name: strawberry.auto
    label: strawberry.auto

    @strawberry.field
    def qbank_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.qbank_id))

    @strawberry.field
    def choices(self, info: Info) -> list[QBChoiceType]:
        return info.context.dl.qbank.load_choices.load(self.id)

    @staticmethod
    def get_queryset(_, queryset: models.QuerySet | None, info: Info):
        return get_queryset_for_model(QBChoiceCollection, queryset)


@strawberry_django.type(QBQuestion)
class QBQuestionType:
    id: strawberry.ID
    name: strawberry.auto
    label: strawberry.auto
    hint: strawberry.auto
    order: strawberry.auto

    default: strawberry.auto
    guidance_hint: strawberry.auto
    trigger: strawberry.auto
    readonly: strawberry.auto
    required: strawberry.auto
    required_message: strawberry.auto
    relevant: strawberry.auto
    constraint: strawberry.auto
    appearance: strawberry.auto
    calculation: strawberry.auto
    parameters: strawberry.auto
    choice_filter: strawberry.auto
    image: strawberry.auto
    video: strawberry.auto
    is_or_other: strawberry.auto

    type = enum_field(QBQuestion.type)
    type_display = enum_display_field(QBQuestion.type)
    # Qber Metadata
    priority_level = enum_field(QBQuestion.priority_level)
    priority_level_display = enum_display_field(QBQuestion.priority_level)
    enumerator_skill = enum_field(QBQuestion.enumerator_skill)
    enumerator_skill_display = enum_display_field(QBQuestion.enumerator_skill)
    data_collection_method = enum_field(QBQuestion.data_collection_method)
    data_collection_method_display = enum_display_field(QBQuestion.data_collection_method)
    required_duration: strawberry.auto

    @staticmethod
    def get_queryset(_, queryset: models.QuerySet | None, info: Info):
        return get_queryset_for_model(QBQuestion, queryset)

    @strawberry.field
    def qbank_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.qbank_id))

    @strawberry.field
    def leaf_group_id(self) -> typing.Optional[strawberry.ID]:
        if self.leaf_group_id:
            return strawberry.ID(str(self.leaf_group_id))

    @strawberry.field
    def choice_collection_id(self) -> typing.Optional[int]:
        return self.choice_collection_id
