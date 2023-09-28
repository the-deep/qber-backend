import typing

from django.db import models
from django.core.exceptions import ValidationError

from apps.common.models import UserResource
from utils.common import get_current_datetime_str

from .base_models import (
    BaseChoiceCollection,
    BaseChoice,
    BaseQuestion,
    BaseQuestionLeafGroup,
)


def import_file_upload_to(_: 'QuestionBank', filename: str) -> str:
    time_str = get_current_datetime_str()
    return f'import/qbank/{time_str}/{filename}'


class QuestionBank(UserResource):
    class Status(models.IntegerChoices):
        PENDING = 1, 'Pending'
        STARTED = 2, 'Started'
        SUCCESS = 3, 'Success'
        FAILURE = 4, 'Failure'

    title = models.CharField(max_length=255)
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.PENDING)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    import_file = models.FileField(
        upload_to=import_file_upload_to,
        help_text='XLSForm',
        max_length=255,
    )

    def __str__(self):
        return f'{self.pk}: {self.title}'

    def activate(self):
        if self.status != self.Status.SUCCESS:
            raise ValidationError('QuestionBank status should be success')
        type(self).objects.filter(is_active=True).update(is_active=False)
        self.is_active = True
        self.save(update_fields=('is_active',))

    @classmethod
    def get_active(cls) -> typing.Self | None:
        return cls.objects.filter(is_active=True).order_by('-id').first()


class QBChoiceCollection(BaseChoiceCollection):
    qbank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    qbchoice_set: models.QuerySet['QBChoice']

    class Meta:
        unique_together = ('qbank', 'name')


class QBChoice(BaseChoice):
    collection = models.ForeignKey(QBChoiceCollection, on_delete=models.CASCADE)

    collection_id: int

    class Meta:
        unique_together = ('collection', 'name')


class QBLeafGroup(BaseQuestionLeafGroup):
    qbank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    hide_in_framework = models.BooleanField(default=False)

    class Meta:
        unique_together = ('qbank', 'name')

    @property
    def existing_leaf_groups_qs(self) -> models.QuerySet[typing.Self]:
        return QBLeafGroup.objects.filter(
            # Scope by qbank
            qbank=self.qbank,
        )

    @classmethod
    def check_if_hidden_in_framework(cls, _type, c1, c2, c3, c4) -> bool:
        if _type == cls.Type.MATRIX_1D:
            return c2 in (
                cls.CATEGORIES_HIDDEN_IN_FRAMEWORK_MAP[_type].get(c1, {})
            )
        elif _type == cls.Type.MATRIX_2D:
            return (
                c2 in (
                    cls.CATEGORIES_HIDDEN_IN_FRAMEWORK_MAP
                    [cls.Type.MATRIX_2D]
                    ['rows']
                    .get(c1, {})
                ) or
                c4 in (
                    cls.CATEGORIES_HIDDEN_IN_FRAMEWORK_MAP
                    [cls.Type.MATRIX_2D]
                    ['columns']
                    .get(c3, {})
                )
            )
        return False


class QBQuestion(BaseQuestion):
    qbank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    leaf_group = models.ForeignKey(QBLeafGroup, on_delete=models.CASCADE, null=True, blank=True)
    choice_collection = models.ForeignKey(
        QBChoiceCollection,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
