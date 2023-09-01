from django.db import models

from apps.common.models import UserResource
from apps.questionnaire.models import (
    ChoiceCollection,
    Choice,
    QuestionGroup,
    Question,
)


class QuestionBank(UserResource):
    title = models.CharField(max_length=255)
    is_draft = models.BooleanField(default=True)


class QBChoiceCollection(ChoiceCollection):
    questionnaire = None
    qbank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    choice_set: models.QuerySet['QBChoice']

    class Meta:
        unique_together = ('qbank', 'name')


class QBChoice(Choice):
    collection = models.ForeignKey(QBChoiceCollection, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('collection', 'name')


class QBGroup(QuestionGroup):
    questionnaire = None
    qbank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('qbank', 'name')


class QBQuestion(Question):
    questionnaire = None
    qbank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    group = models.ForeignKey(QBGroup, on_delete=models.CASCADE, null=True, blank=True)
    choice_collection = models.ForeignKey(
        QBChoiceCollection,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
