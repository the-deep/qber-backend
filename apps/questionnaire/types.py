import strawberry
import strawberry_django
from strawberry.types import Info
from django.db import models

from utils.common import get_queryset_for_model
from apps.project.models import Project

from .models import Questionnaire


@strawberry_django.type(Questionnaire)
class QuestionnaireType:
    id: strawberry.ID
    title: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto
    created_by: strawberry.auto
    modified_by: strawberry.auto

    @staticmethod
    def get_queryset(_, queryset: models.QuerySet | None, info: Info):
        qs = get_queryset_for_model(Questionnaire, queryset)
        if (
            info.context.active_project and
            info.context.has_perm(Project.Permission.VIEW_QUESTIONNAIRE)
        ):
            return qs.filter(
                project=info.context.active_project.project,
            )
        return qs.none()

    @strawberry.field
    def project_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.project_id))
