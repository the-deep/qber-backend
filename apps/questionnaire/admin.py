from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilterFactory

from .models import (
    Questionnaire,
    Question,
    QuestionLeafGroup,
)


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = (
        'title',
        'project',
        'created_at',
    )
    list_filter = (
        AutocompleteFilterFactory('Project', 'project'),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = (
        'name',
        'created_at',
    )
    list_filter = (
        AutocompleteFilterFactory('Questionnaire', 'questionnaire'),
    )


@admin.register(QuestionLeafGroup)
class QuestionLeafGroupAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = (
        'name',
        'order',
        'type',
        'category_1',
        'category_2',
        'category_3',
        'category_4',
        'relevant',
    )
    list_filter = (
        AutocompleteFilterFactory('Questionnaire', 'questionnaire'),
        'type',
        'category_1',
        'category_2',
        'category_3',
        'category_4',
    )
