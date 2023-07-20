from django.contrib import admin

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
