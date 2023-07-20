import strawberry
import strawberry_django

from .models import Questionnaire


@strawberry_django.filters.filter(Questionnaire, lookups=True)
class QuestionnaireFilter:
    id: strawberry.auto
    project: strawberry.auto
    search: str | None

    def filter_search(self, queryset):
        if self.search:
            queryset = queryset.filter(
                title__icontains=self.search,
            )
        return queryset
