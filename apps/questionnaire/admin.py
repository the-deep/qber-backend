from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilterFactory

from .models import (
    Questionnaire,
    Question,
    ChoiceCollection,
    QuestionLeafGroup,
    Choice,
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


class ChoiceAdminInline(admin.TabularInline):
    model = Choice
    search_fields = ('name',)
    extra = 0
    autocomplete_fields = ('collection',)


@admin.register(ChoiceCollection)
class ChoiceCollectionAdmin(admin.ModelAdmin):
    search_fields = ('name', 'label')
    list_display = (
        'name',
        'label',
        'questionnaire_id',
    )
    list_filter = (
        AutocompleteFilterFactory('Questionnaire', 'questionnaire'),
    )
    inlines = (
        ChoiceAdminInline,
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
