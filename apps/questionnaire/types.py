import typing
import strawberry
import strawberry_django
from strawberry.types import Info
from django.db import models

from utils.common import get_queryset_for_model, resolve_field_relation
from utils.strawberry.enums import enum_display_field, enum_field
from apps.common.types import UserResourceTypeMixin, ClientIdMixin
from apps.project.models import Project
from apps.qbank.types import QuestionBankType

from .models import (
    Questionnaire,
    Question,
    QuestionLeafGroup,
    ChoiceCollection,
    Choice,
)


@strawberry.type
class QuestionCount:
    total: int = 0
    visible: int = 0


@strawberry_django.type(QuestionLeafGroup)
class QuestionLeafGroupType(UserResourceTypeMixin):
    id: strawberry.ID
    name: strawberry.auto
    type = enum_field(QuestionLeafGroup.type)
    type_display = enum_display_field(QuestionLeafGroup.type)
    order: strawberry.auto
    is_hidden: strawberry.auto
    # Categories
    # -- For Matrix1D/Matrix2D
    category_1 = enum_field(QuestionLeafGroup.category_1)
    category_1_display = enum_display_field(QuestionLeafGroup.category_1)
    category_2 = enum_field(QuestionLeafGroup.category_2)
    category_2_display = enum_display_field(QuestionLeafGroup.category_2)
    # -- For Matrix2D
    category_3 = enum_field(QuestionLeafGroup.category_3)
    category_3_display = enum_display_field(QuestionLeafGroup.category_3)
    category_4 = enum_field(QuestionLeafGroup.category_4)
    category_4_display = enum_display_field(QuestionLeafGroup.category_4)
    # Misc
    relevant: strawberry.auto

    @strawberry.field
    def questionnaire_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.questionnaire_id))

    @staticmethod
    def get_queryset(_, queryset: models.QuerySet | None, info: Info):
        qs = get_queryset_for_model(QuestionLeafGroup, queryset)
        if (
            info.context.active_project and
            info.context.has_perm(Project.Permission.VIEW_QUESTION_GROUP)
        ):
            return qs.filter(questionnaire__project=info.context.active_project.project)
        return qs.none()

    @strawberry.field
    def qbank_leaf_group_id(self) -> strawberry.ID | None:
        if self.qbank_leaf_group_id:
            return strawberry.ID(str(self.qbank_leaf_group_id))

    @strawberry.field
    def total_qbank_questions(self, info: Info) -> int | None:
        if self.qbank_leaf_group_id:
            return info.context.dl.qbank.total_questions_by_leaf_group.load(self.qbank_leaf_group_id)

    @strawberry.field
    def total_questions(self, info: Info) -> QuestionCount:
        return info.context.dl.questionnaire.total_questions_by_leaf_group.load(self.id)


@strawberry_django.type(Questionnaire)
class QuestionnaireType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    # Qber Metadata
    priority_levels = enum_field(Questionnaire.priority_levels)
    priority_levels_display = enum_display_field(Questionnaire.priority_levels)
    enumerator_skills = enum_field(Questionnaire.enumerator_skills)
    enumerator_skills_display = enum_display_field(Questionnaire.enumerator_skills)
    data_collection_methods = enum_field(Questionnaire.data_collection_methods)
    data_collection_methods_display = enum_display_field(Questionnaire.data_collection_methods)

    required_duration: strawberry.auto

    @staticmethod
    def get_queryset(_, queryset: models.QuerySet | None, info: Info):
        qs = get_queryset_for_model(Questionnaire, queryset)
        if (
            info.context.active_project and
            info.context.has_perm(Project.Permission.VIEW_QUESTIONNAIRE)
        ):
            return qs.filter(project=info.context.active_project.project)
        return qs.none()

    @strawberry.field
    def project_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.project_id))

    @strawberry_django.field
    async def leaf_groups(self, info: Info) -> list[QuestionLeafGroupType]:
        queryset = QuestionLeafGroupType.get_queryset(None, None, info).filter(questionnaire=self.pk)
        return [q async for q in queryset]

    @strawberry_django.field
    async def choice_collections(self, info: Info) -> list['QuestionChoiceCollectionType']:
        queryset = QuestionChoiceCollectionType.get_queryset(None, None, info).filter(questionnaire=self.pk)
        return [q async for q in queryset]

    @strawberry.field
    def total_questions(self, info: Info) -> QuestionCount:
        return info.context.dl.questionnaire.total_questions_by_questionnaire.load(self.id)

    @strawberry.field
    def qbank(self, info: Info) -> QuestionBankType:
        return resolve_field_relation(
            self,
            'qbank',
            info.context.dl.questionnaire.load_qbank.load,
        )

    @strawberry.field
    def total_qbank_questions(self, info: Info) -> int:
        return info.context.dl.qbank.total_questions_by_qbank.load(self.qbank_id)


@strawberry_django.type(Choice)
class QuestionChoiceType(ClientIdMixin):
    id: strawberry.ID
    name: strawberry.auto
    label: strawberry.auto
    # geometry: strawberry.auto

    @strawberry.field
    def collection_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.collection_id))


@strawberry_django.type(ChoiceCollection)
class QuestionChoiceCollectionType(UserResourceTypeMixin):
    id: strawberry.ID
    name: strawberry.auto
    label: strawberry.auto

    @strawberry.field
    def questionnaire_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.questionnaire_id))

    @strawberry.field
    def choices(self, info: Info) -> list[QuestionChoiceType]:
        return info.context.dl.questionnaire.load_choices.load(self.id)

    @staticmethod
    def get_queryset(_, queryset: models.QuerySet | None, info: Info):
        qs = get_queryset_for_model(ChoiceCollection, queryset)
        if (
            info.context.active_project and
            info.context.has_perm(Project.Permission.VIEW_QUESTION_CHOICE)
        ):
            return qs.filter(questionnaire__project=info.context.active_project.project)
        return qs.none()


@strawberry_django.type(Question)
class QuestionType(UserResourceTypeMixin):
    id: strawberry.ID
    name: strawberry.auto
    label: strawberry.auto
    hint: strawberry.auto
    order: strawberry.auto
    is_hidden: strawberry.auto

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

    type = enum_field(Question.type)
    type_display = enum_display_field(Question.type)
    # Qber Metadata
    priority_level = enum_field(Question.priority_level)
    priority_level_display = enum_display_field(Question.priority_level)
    enumerator_skill = enum_field(Question.enumerator_skill)
    enumerator_skill_display = enum_display_field(Question.enumerator_skill)
    data_collection_method = enum_field(Question.data_collection_method)
    data_collection_method_display = enum_display_field(Question.data_collection_method)
    required_duration: strawberry.auto

    @staticmethod
    def get_queryset(_, queryset: models.QuerySet | None, info: Info):
        qs = get_queryset_for_model(Question, queryset)
        if (
            info.context.active_project and
            info.context.has_perm(Project.Permission.VIEW_QUESTION)
        ):
            return qs.filter(questionnaire__project=info.context.active_project.project)
        return qs.none()

    @strawberry.field
    def questionnaire_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.questionnaire_id))

    @strawberry.field
    def leaf_group_id(self) -> typing.Optional[strawberry.ID]:
        if self.leaf_group_id:
            return strawberry.ID(str(self.leaf_group_id))

    @strawberry.field
    def choice_collection_id(self) -> typing.Optional[strawberry.ID]:
        if self.choice_collection_id:
            return strawberry.ID(str(self.choice_collection_id))
