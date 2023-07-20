from django.db import models

from utils.common import get_queryset_for_model
from apps.common.models import UserResource
from apps.project.models import Project


class Questionnaire(UserResource):
    title = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    project_id: int

    @classmethod
    def get_for(cls, user, queryset=None):
        project_qs = Project.get_for(user)
        return get_queryset_for_model(cls, queryset=queryset).filter(project__in=project_qs)
