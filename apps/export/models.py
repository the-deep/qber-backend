import typing

from django.db import models
from django.utils import timezone
from django.core.cache import cache

from main.celery import app as celery_app
from main.caches import CacheKey
from apps.user.models import User
from apps.questionnaire.models import Questionnaire


def questionnaire_export_file_upload_to(_: 'QuestionnaireExport', filename: str) -> str:
    time_str = timezone.now().strftime('%Y-%m-%d%z')
    return f'export/questionnaire/{time_str}/{filename}'


class QuestionnaireExport(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 1, 'Pending'
        STARTED = 2, 'Started'
        SUCCESS = 3, 'Success'
        FAILURE = 4, 'Failure'
        CANCELED = 5, 'Canceled'

    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    exported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    exported_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    status: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.PENDING)

    # Files
    xlsx_file = models.FileField(
        upload_to=questionnaire_export_file_upload_to,
        max_length=255,
        null=True,
        blank=True,
        default=None,
    )
    xml_file = models.FileField(
        upload_to=questionnaire_export_file_upload_to,
        max_length=255,
        null=True,
        blank=True,
        default=None,
    )

    questionnaire_id: int
    exported_by_id: int
    get_type_display: typing.Callable[..., str]
    get_status_display: typing.Callable[..., str]

    def __str__(self):
        return f'Q:{self.questionnaire_id} @ U:{self.exported_by_id}'

    def set_task_id(self, async_id: str):
        return cache.set(
            CacheKey.EXPORT_TASK_ID_CACHE_KEY.format(self.pk),
            async_id,
            86400,  # 1 Day
        )

    def get_task_id(self, clear=False):
        cache_key = CacheKey.EXPORT_TASK_ID_CACHE_KEY.format(self.pk)
        value = cache.get(cache_key)
        if clear:
            cache.delete(cache_key)
        return value

    def cancel(self, commit=True):
        if self.status not in [self.Status.PENDING, self.Status.STARTED]:
            return
        celery_app.control.revoke(
            self.get_task_id(clear=True),
            terminate=True,
        )
        self.status = self.Status.CANCELED
        if commit:
            self.save(update_fields=('status',))
