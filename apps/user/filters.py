import strawberry
import strawberry_django
from django.db import models
from django.db.models.functions import Concat

from .models import User


@strawberry_django.filters.filter(User, lookups=True)
class UserFilter:
    id: strawberry.auto
    search: str | None

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
