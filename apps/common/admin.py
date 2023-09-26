from django.conf import settings


class ReadOnlyMixin():
    def has_add_permission(self, *args, **kwargs):
        return settings.ENABLE_BREAKING_MODE

    def has_change_permission(self, *args, **kwargs):
        return settings.ENABLE_BREAKING_MODE

    def has_delete_permission(self, *args, **kwargs):
        return settings.ENABLE_BREAKING_MODE
