import typing
import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from strawberry.types import Info
from django.db import models

from utils.common import get_queryset_for_model
from apps.common.types import UserResourceTypeMixin, ClientIdMixin
from apps.project.models import Project

from .enums import QuestionTypeEnum
from .models import (
    Questionnaire,
    Question,
    QuestionGroup,
    ChoiceCollection,
    Choice,
)


@strawberry_django.type(Questionnaire)
class QuestionnaireType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto

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


@strawberry_django.type(QuestionGroup)
class QuestionGroupType(UserResourceTypeMixin):
    id: strawberry.ID
    name: strawberry.auto
    label: strawberry.auto
    relevant: strawberry.auto

    @strawberry.field
    def questionnaire_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.questionnaire_id))

    @strawberry.field
    def parent_id(self) -> typing.Optional[strawberry.ID]:
        return self.parent_id and strawberry.ID(str(self.parent_id))

    @staticmethod
    def get_queryset(_, queryset: models.QuerySet | None, info: Info):
        qs = get_queryset_for_model(QuestionGroup, queryset)
        if (
            info.context.active_project and
            info.context.has_perm(Project.Permission.VIEW_QUESTION_GROUP)
        ):
            return qs.filter(questionnaire__project=info.context.active_project.project)
        return qs.none()


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
    async def choices(self) -> list[QuestionChoiceType]:
        # TODO: Use Dataloaders
        return [
            choice
            async for choice in self.choice_set.order_by('id')
        ]

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
    or_other_label: strawberry.auto

    type: QuestionTypeEnum

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
    def group_id(self) -> typing.Optional[strawberry.ID]:
        if self.group_id:
            return strawberry.ID(str(self.group_id))

    @strawberry.field
    @sync_to_async
    def choice_collection(self) -> typing.Optional[QuestionChoiceCollectionType]:
        # TODO: Dataloader
        return self.choice_collection
