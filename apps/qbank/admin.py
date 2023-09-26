from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilterFactory

from apps.common.admin import ReadOnlyMixin
from .models import (
    QuestionBank,
    QBQuestion,
    QBChoiceCollection,
    QBChoice,
    QBLeafGroup,
)


@admin.register(QuestionBank)
class QuestionBankAdmin(ReadOnlyMixin, admin.ModelAdmin):
    search_fields = ('title',)
    list_display = (
        '__str__',
        'created_at',
        'is_draft',
    )
    list_filter = (
        AutocompleteFilterFactory('Created By', 'created_by'),
        'is_draft',
    )


@admin.register(QBQuestion)
class QBQuestionAdmin(ReadOnlyMixin, admin.ModelAdmin):
    search_fields = ('name', 'label',)
    list_display = (
        'name',
        'label',
        'leaf_group',
        'priority_level',
        'enumerator_skill',
        'data_collection_method',
        'required_duration',
    )
    list_filter = (
        AutocompleteFilterFactory('QuestionBank', 'qbank'),
    )


class QBChoiceAdminInline(ReadOnlyMixin, admin.TabularInline):
    model = QBChoice
    search_fields = ('name',)
    extra = 0
    autocomplete_fields = ('collection',)


@admin.register(QBChoiceCollection)
class QBChoiceCollectionAdmin(ReadOnlyMixin, admin.ModelAdmin):
    search_fields = ('name',)
    list_display = (
        'name',
    )
    list_filter = (
        AutocompleteFilterFactory('QuestionBank', 'qbank'),
    )
    inlines = (
        QBChoiceAdminInline,
    )


@admin.register(QBLeafGroup)
class QBLeafGroupAdmin(ReadOnlyMixin, admin.ModelAdmin):
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
        AutocompleteFilterFactory('QuestionBank', 'qbank'),
        'type',
        'category_1',
        'category_2',
        'category_3',
        'category_4',
    )
