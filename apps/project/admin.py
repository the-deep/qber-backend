from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilterFactory

from .models import Project, ProjectMembership


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 0
    autocomplete_fields = ('added_by', 'member',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = (
        'title',
        'created_at',
    )
    inlines = (ProjectMembershipInline,)
    list_filter = (
        AutocompleteFilterFactory('Creator', 'created_by'),
    )
