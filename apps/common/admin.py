from django.contrib import admin
from django.db import models
from django.conf import settings
from admin_auto_filters.filters import AutocompleteFilterFactory

from .models import GlobalPermission


class ReadOnlyMixin():
    def has_add_permission(self, *args, **kwargs):
        return settings.ENABLE_BREAKING_MODE

    def has_change_permission(self, *args, **kwargs):
        return settings.ENABLE_BREAKING_MODE

    def has_delete_permission(self, *args, **kwargs):
        return settings.ENABLE_BREAKING_MODE


@admin.register(GlobalPermission)
class GlobalPermissionAdmin(admin.ModelAdmin):
    search_fields = ('type',)
    list_display = (
        'type',
        'user_count',
    )
    list_filter = (
        AutocompleteFilterFactory('User', 'users'),
    )
    autocomplete_fields = ('users',)

    def user_count(self, instance):
        if not instance:
            return
        return instance.user_count

    user_count.short_description = 'User Count'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            user_count=models.Subquery(
                GlobalPermission.users.through.objects
                .filter(globalpermission=models.OuterRef('pk'))
                .order_by().values('globalpermission')
                .annotate(
                    count=models.Count('user'),
                ).values('count')[:1],
                output_field=models.IntegerField(),
            ),
        )
