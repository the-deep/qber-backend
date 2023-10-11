from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilterFactory

from .models import QuestionnaireExport


@admin.register(QuestionnaireExport)
class QuestionnaireExportAdmin(admin.ModelAdmin):
    search_fields = ('questionnaire__title',)
    list_display = (
        '__str__',
        'exported_at',
    )
    list_filter = (
        AutocompleteFilterFactory('Owner', 'exported_by'),
    )
