import strawberry
import strawberry_django
from strawberry.types import Info
from django.db import models

from utils.common import get_queryset_for_model
from apps.common.types import UserResourceTypeMixin
from apps.project.models import Project

from .enums import QuestionTypeEnum
from .models import (
    Questionnaire,
    Question,
)


@strawberry_django.ordering.order(Question)
class QuestionOrder:
    id: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.ordering.order(Questionnaire)
class QuestionnaireOrder:
    id: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.type(Question)
class QuestionType(UserResourceTypeMixin):
    id: strawberry.ID
    name: strawberry.auto
    label: strawberry.auto
    hint: strawberry.auto

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
