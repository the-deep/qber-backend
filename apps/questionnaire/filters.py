import strawberry
import strawberry_django

from .models import Questionnaire, Question


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


@strawberry_django.filters.filter(Question, lookups=True)
class QuestionFilter:
    id: strawberry.auto
    questionnaire: strawberry.auto
    name: strawberry.auto
    search: str | None

    def filter_search(self, queryset):
        if self.search:
            queryset = queryset.filter(
                label__icontains=self.search,
            )
        return queryset
