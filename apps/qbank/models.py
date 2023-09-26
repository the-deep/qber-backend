import typing

from django.db import models

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
    title = models.CharField(max_length=255)
    is_draft = models.BooleanField(default=True)
    import_file = models.FileField(
        upload_to=import_file_upload_to,
        help_text='XLSForm',
        max_length=255,
    )


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

    class Meta:
        unique_together = ('qbank', 'name')

    @property
    def existing_leaf_groups_qs(self) -> models.QuerySet[typing.Self]:
        return QBLeafGroup.objects.filter(
            # Scope by qbank
            qbank=self.qbank,
        )


class QBQuestion(BaseQuestion):
    qbank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    leaf_group = models.ForeignKey(QBLeafGroup, on_delete=models.CASCADE, null=True, blank=True)
    choice_collection = models.ForeignKey(
        QBChoiceCollection,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
