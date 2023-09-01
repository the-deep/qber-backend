from django import template
from django.conf import settings
from django.templatetags.static import static
from django.core.files.storage import FileSystemStorage, storages


register = template.Library()

DEFAULT_BACKEND_STORAGE = storages.backends['staticfiles']


@register.filter(is_safe=True)
def static_full_path(path):
    static_path = static(path)
    if isinstance(DEFAULT_BACKEND_STORAGE, FileSystemStorage):
        return f"{settings.APP_HTTP_PROTOCOL}://{settings.APP_DOMAIN}{static_path}"
    # With s3 storage
    return static_path
