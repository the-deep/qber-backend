import functools
from enum import Enum, auto, unique
from django.db import models

from utils.common import get_queryset_for_model
from apps.common.models import UserResource
from apps.user.models import User


class ProjectMembership(models.Model):
    class Role(models.IntegerChoices):
        ADMIN = 1, 'Admin'
        MEMBER = 2, 'Member'
        VIEWER = 3, 'Viewer'

    member = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey('project.Project', on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=Role.choices, default=Role.MEMBER)

    joined_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='added_project_memberships',
    )

    member_id: int
    project_id: int
    added_by_id: int

    class Meta:
        unique_together = ('member', 'project')

    def __str__(self):
        return '{} @ {}'.format(str(self.member), self.project.title)


class Project(UserResource):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    members = models.ManyToManyField(
        User,
        blank=True,
        through_fields=('project', 'member'),
        through='ProjectMembership',
    )

    @unique
    class Permission(Enum):
        # Project
        UPDATE_PROJECT = auto()
        UPDATE_MEMBERSHIPS = auto()
        # Questionnaire
        VIEW_QUESTIONNAIRE = auto()
        EXPORT_QUESTIONNAIRE = auto()
        CREATE_QUESTIONNAIRE = auto()
        UPDATE_QUESTIONNAIRE = auto()
        DELETE_QUESTIONNAIRE = auto()
        # Question
        VIEW_QUESTION = auto()
        CREATE_QUESTION = auto()
        UPDATE_QUESTION = auto()
        DELETE_QUESTION = auto()
        # Question Group
        VIEW_QUESTION_GROUP = auto()
        CREATE_QUESTION_GROUP = auto()
        UPDATE_QUESTION_GROUP = auto()
        DELETE_QUESTION_GROUP = auto()
        # Question Choice
        VIEW_QUESTION_CHOICE = auto()
        CREATE_QUESTION_CHOICE = auto()
        UPDATE_QUESTION_CHOICE = auto()
        DELETE_QUESTION_CHOICE = auto()

    @classmethod
    @functools.lru_cache
    def get_permissions(cls) -> dict[ProjectMembership.Role, list[Permission]]:
        return {
            ProjectMembership.Role.ADMIN: [
                permission
                for permission in cls.Permission
            ],
            ProjectMembership.Role.MEMBER: [
                permission
                for permission in cls.Permission
                if permission not in [
                    cls.Permission.UPDATE_PROJECT,
                    cls.Permission.UPDATE_MEMBERSHIPS,
                ]
            ],
            ProjectMembership.Role.VIEWER: [
                cls.Permission.VIEW_QUESTIONNAIRE,
                cls.Permission.VIEW_QUESTION,
                cls.Permission.VIEW_QUESTION_GROUP,
                cls.Permission.VIEW_QUESTION_CHOICE,
            ],
        }

    def __str__(self):
        return self.title

    def get_permissions_for_user(self, user: User):
        membership = ProjectMembership.objects.filter(
            member=user,
            project=self,
        ).first()
        if membership:
            return self.get_permissions().get(membership.role, [])
        return []

    @classmethod
    def get_for(cls, user, queryset=None):
        current_user_role_subquery = models.Subquery(
            ProjectMembership.objects.filter(
                project=models.OuterRef('pk'),
                member=user,
            ).order_by('role').values('role')[:1],
            output_field=models.CharField(),
        )

        return get_queryset_for_model(cls, queryset=queryset).annotate(
            # For using within query filters
            current_user_role=current_user_role_subquery,
        ).exclude(current_user_role__isnull=True)

    def add_member(
        self,
        user,
        role: ProjectMembership.Role | None = ProjectMembership.Role.MEMBER,
        added_by: User | None = None,
    ):
        """
        Add or update existing membership for given user and role
        """
        existing_membership, _ = ProjectMembership.objects.get_or_create(
            project=self,
            member=user,
        )
        existing_membership.role = role
        existing_membership.added_by = added_by
        existing_membership.save(update_fields=('role', 'added_by'))
        return existing_membership
