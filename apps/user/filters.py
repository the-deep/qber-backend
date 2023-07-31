import strawberry
import strawberry_django
from strawberry.types import Info
from django.db import models
from django.db.models.functions import Concat

from .models import User


@strawberry_django.filters.filter(User, lookups=True)
class UserFilter:
    id: strawberry.auto
    search: str | None
    members_exclude_project: strawberry.ID | None
    exclude_me: bool = False

    def filter_search(self, queryset):
        value = self.search
        if value:
            queryset = queryset.annotate(
                full_name=Concat(
                    models.F("first_name"),
                    models.Value(" "),
                    models.F("last_name"),
                    output_field=models.CharField(),
                )
            ).filter(
                models.Q(full_name__icontains=value) |
                models.Q(first_name__icontains=value) |
                models.Q(last_name__icontains=value) |
                models.Q(email__icontains=value)
            )
        return queryset

    def filter_members_exclude_project(self, queryset):
        value = self.members_exclude_project
        if value:
            queryset = queryset.filter(
                ~models.Q(projectmembership__project_id=value)
            ).distinct()
        return queryset

    def filter_exclude_me(self, queryset, info: Info):
        value = self.exclude_me
        if value:
            queryset = queryset.exclude(id=info.context.request.user.id)
        return queryset
