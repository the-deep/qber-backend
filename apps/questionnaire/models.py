import typing
from django.db import models
from django.contrib.postgres.fields import ArrayField

from utils.common import get_queryset_for_model
from apps.user.models import User
from apps.common.models import UserResource
from apps.project.models import Project
from apps.qbank.base_models import (
    QberMetaData,
    # -- Base
    BaseChoiceCollection,
    BaseChoice,
    BaseQuestion,
    BaseQuestionLeafGroup,
)
from apps.qbank.models import (
    # -- Qbank
    QuestionBank,
    QBChoiceCollection,
    QBChoice,
    QBLeafGroup,
    QBQuestion,
)


class Questionnaire(QberMetaData, UserResource):
    title = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    qbank = models.ForeignKey(
        QuestionBank,
        on_delete=models.PROTECT,
        related_name='+',
    )

    # QberMetaData
    priority_level = None
    enumerator_skills = None
    data_collection_methods = None
    # -- Multiple
    priority_levels = ArrayField(
        models.PositiveSmallIntegerField(choices=QberMetaData.PriorityLevel.choices),
        blank=True,
        default=list,
    )
    enumerator_skills = ArrayField(
        models.PositiveSmallIntegerField(choices=QberMetaData.EnumeratorSkill.choices),
        blank=True,
        default=list,
    )
    data_collection_methods = ArrayField(
        models.PositiveSmallIntegerField(choices=QberMetaData.DataCollectionMethod.choices),
        blank=True,
        default=list,
    )

    project_id: int
    qbank_id: int
    question_set: models.QuerySet['Question']

    def __str__(self):
        return self.title

    @classmethod
    def get_for(cls, user, queryset=None):
        project_qs = Project.get_for(user)
        return get_queryset_for_model(cls, queryset=queryset).filter(project__in=project_qs)

    def delete(self):
        # Delete questions first as question depends on other attributes which will through PROTECT error
        self.question_set.all().delete()
        return super().delete()


class ChoiceCollection(BaseChoiceCollection, UserResource):
    qbank_choice_collection = models.ForeignKey(
        QBChoiceCollection,
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True,
    )
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    choice_set: models.QuerySet['Choice']

    class Meta:
        unique_together = ('questionnaire', 'name')

    @classmethod
    def clone_from_qb_choice_collection(
        cls,
        qbank_choice_collection: QBChoiceCollection,
        questionnaire: Questionnaire,
        user: User,
    ) -> typing.Self:
        choice_collection = ChoiceCollection.objects.create(
            # From Qbank ChoiceCollection
            **{
                key: value
                for key, value in qbank_choice_collection.__dict__.items()
                if key not in {
                    '_state',
                    'id',
                    'qbank_id',
                }
            },
            qbank_choice_collection=qbank_choice_collection,
            questionnaire=questionnaire,
            created_by=user,
            modified_by=user,
        )
        # Now choices
        for qbank_choice in qbank_choice_collection.qbchoice_set.all():
            # TODO: Bulk create is having issue with unique_together
            Choice.objects.create(
                # From Qbank ChoiceCollection
                **{
                    key: value
                    for key, value in qbank_choice.__dict__.items()
                    if key not in {
                        '_state',
                        'id',
                        'collection_id',
                    }
                },
                qbank_choice=qbank_choice,
                collection=choice_collection,
            )
        return choice_collection


class Choice(BaseChoice):
    qbank_choice = models.ForeignKey(
        QBChoice,
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True,
    )
    collection = models.ForeignKey(ChoiceCollection, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('collection', 'name')


class QuestionLeafGroup(BaseQuestionLeafGroup, UserResource):
    qbank_leaf_group = models.ForeignKey(
        QBLeafGroup,
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True,
    )
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        unique_together = [
            ('questionnaire', 'name'),
            ('questionnaire', 'category_1', 'category_2', 'category_3', 'category_4'),
        ]
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['order']),
        ]
        ordering = ('order',)

    @property
    def existing_leaf_groups_qs(self) -> models.QuerySet[typing.Self]:
        return QuestionLeafGroup.objects.filter(
            # Scope by questionnaire
            questionnaire=self.questionnaire,
        )

    @classmethod
    def clone_from_qbank(
        cls,
        questionnaire: Questionnaire,
        user: User,
    ) -> None:
        assert questionnaire.qbank is not None
        # Create initial leaf groups using qbank
        new_leaf_groups = []
        for qbank_leaf_group in questionnaire.qbank.qbleafgroup_set.all():
            new_leaf_groups.append(
                cls(
                    # From Qbank Leaf Group
                    **{
                        key: value
                        for key, value in qbank_leaf_group.__dict__.items()
                        if key not in {
                            '_state',
                            'id',
                            'qbank_id',
                            'hide_in_framework',
                        }
                    },
                    is_hidden=True,
                    qbank_leaf_group=qbank_leaf_group,
                    created_by=user,
                    modified_by=user,
                    questionnaire=questionnaire,
                )
            )
        cls.objects.bulk_create(new_leaf_groups)


class Question(BaseQuestion, UserResource):
    qbank_question = models.ForeignKey(
        QBQuestion,
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True,
    )
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    is_hidden = models.BooleanField(default=False)
    leaf_group = models.ForeignKey(QuestionLeafGroup, on_delete=models.CASCADE)
    choice_collection = models.ForeignKey(
        ChoiceCollection,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ('questionnaire', 'name')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['order']),
        ]
        ordering = ('leaf_group__order', 'order',)

    @classmethod
    def clone_from_qb_leaf_group(
        cls,
        leaf_group: QuestionLeafGroup,
        user: User,
    ) -> None:
        # Qbank Choice Collection ID -> Questionnaire Choice Collection ID
        new_choice_collections_map = {
            qbank_choice_collection_id: _id
            for _id, qbank_choice_collection_id in (
                leaf_group
                .questionnaire
                .choicecollection_set
                .filter(qbank_choice_collection__isnull=False)
                .values_list('id', 'qbank_choice_collection')
            )
        }

        assert leaf_group.qbank_leaf_group is not None

        def _get_choice_collection_id(choice_collection: QBChoiceCollection) -> None | int:
            if choice_collection is None:
                return
            _id = choice_collection.pk
            if _id in new_choice_collections_map:
                return new_choice_collections_map[_id]
            # XXX: N+1
            new_id = ChoiceCollection.clone_from_qb_choice_collection(
                choice_collection,
                leaf_group.questionnaire,
                user,
            ).pk
            new_choice_collections_map[_id] = new_id
            return new_id

        # Create initial leaf groups using qbank
        new_questions = []
        for qbank_question in leaf_group.qbank_leaf_group.qbquestion_set.select_related('choice_collection').all():
            choice_collection_id = _get_choice_collection_id(qbank_question.choice_collection)
            new_questions.append(
                cls(
                    # From Qbank Questions
                    **{
                        key: value
                        for key, value in qbank_question.__dict__.items()
                        if key not in {
                            '_state',
                            'id',
                            'qbank_id',
                            'leaf_group_id',
                            'choice_collection_id',
                        }
                    },
                    is_hidden=False,
                    leaf_group=leaf_group,
                    choice_collection_id=choice_collection_id,
                    qbank_question=qbank_question,
                    created_by=user,
                    modified_by=user,
                    questionnaire=leaf_group.questionnaire,
                )
            )
        cls.objects.bulk_create(new_questions)
