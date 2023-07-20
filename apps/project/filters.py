import strawberry
import strawberry_django
from django.db import models

from .models import Project, ProjectMembership


@strawberry_django.filters.filter(Project, lookups=True)
class ProjectFilter:
    id: strawberry.auto
    search: str | None

    def filter_search(self, queryset):
        if self.search:
            queryset = queryset.filter(
                title__icontains=self.search,
            )
        return queryset


@strawberry_django.filters.filter(ProjectMembership, lookups=True)
class ProjectMembershipFilter:
    id: strawberry.auto
    search: str | None

    def filter_search(self, queryset):
        if self.search:
            queryset = queryset.filter(
                models.Q(member__email__icontains=self.search) |
                models.Q(member__first_name__icontains=self.search) |
                models.Q(member__last_name__icontains=self.search)
            )
        return queryset
