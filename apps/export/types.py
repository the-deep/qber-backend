import urllib.parse
import strawberry
import strawberry_django
from strawberry.types import Info
from django.db import models
from django.conf import settings

from utils.common import get_queryset_for_model
from utils.strawberry.enums import enum_display_field, enum_field
from apps.common.types import file_field, get_cached_file_uri
from apps.project.models import Project
from apps.user.types import UserType

from .models import QuestionnaireExport


@strawberry_django.type(QuestionnaireExport)
class QuestionnaireExportType:
    id: strawberry.ID

    exported_at: strawberry.auto
    started_at: strawberry.auto
    ended_at: strawberry.auto

    status = enum_field(QuestionnaireExport.status)
    status_display = enum_display_field(QuestionnaireExport.status)

    xlsx_file = file_field(QuestionnaireExport.xlsx_file)
    # http://localhost:8005/preview?form=http%3A%2F%2F127.0.0.1%3A8080%2FQuestionnaire-5_nXuUP4m.xml
    xml_file = file_field(QuestionnaireExport.xml_file)

    @strawberry.field
    @staticmethod
    def enketo_preview_url(root: QuestionnaireExport, info: Info) -> str | None:
        if root.xml_file.name:
            xm_file_url = get_cached_file_uri(
                root.xml_file,
                info.context.request,
            )
            params = {'form': xm_file_url}
            return f'{settings.ENKETO_DOMAIN}/preview?{urllib.parse.urlencode(params)}'

    @strawberry.field
    @staticmethod
    def exported_by(root: QuestionnaireExport, info: Info) -> UserType:
        return info.context.dl.user.load_users.load(root.exported_by_id)

    @strawberry.field
    def questionnaire_id(self) -> strawberry.ID:
        return strawberry.ID(str(self.questionnaire_id))

    @staticmethod
    def get_queryset(_, queryset: models.QuerySet | None, info: Info):
        qs = get_queryset_for_model(QuestionnaireExport, queryset)
        if (
            info.context.active_project and
            info.context.has_perm(Project.Permission.EXPORT_QUESTIONNAIRE)
        ):
            return qs.filter(
                questionnaire__project=info.context.active_project.project,
                exported_by=info.context.request.user,
            )
        return qs.none()
