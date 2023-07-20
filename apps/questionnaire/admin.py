from django.contrib import admin

from .models import Questionnaire


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = (
        'title',
        'project',
        'created_at',
    )
