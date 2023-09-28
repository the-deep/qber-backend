import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from apps.user.models import User
from apps.user.factories import UserFactory
from apps.project.models import Project, ProjectMembership
from apps.project.factories import ProjectFactory
from apps.qbank.models import QBQuestion, QuestionBank, QBLeafGroup
from apps.questionnaire.models import QuestionLeafGroup
from apps.questionnaire.factories import QuestionnaireFactory
from apps.qbank.factories import (
    QuestionBankFactory,
    QBLeafGroupFactory,
    QBQuestionFactory,
    QBChoiceCollectionFactory,
    QBChoiceFactory,
)


class Command(BaseCommand):
    help = 'Load dummy data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-all',
            dest='DELETE_ALL',
            action='store_true',
            default=False,
        )

    def get_or_create_superuser(self):
        user = User.objects.filter(email='admin@test.com').first()
        if user:
            return user
        user = UserFactory.create(
            email='admin@test.com',
            password_text='admin123',
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=('is_staff', 'is_superuser'))
        self.stdout.write(f'Added user with credentials: {user.email}:{user.password_text}')
        return user

    def process_qbank(self, qbank: QuestionBank):
        # Choices
        # -- Collection
        choice_collection_1, choice_collection_2, choice_collection_3 = QBChoiceCollectionFactory.create_batch(
            3,
            qbank=qbank,
        )
        # -- Choices
        QBChoiceFactory.create_batch(10, collection=choice_collection_1)
        QBChoiceFactory.create_batch(5, collection=choice_collection_2)
        QBChoiceFactory.create_batch(7, collection=choice_collection_3)

        # Questions
        group_categories = QBLeafGroupFactory.random_category_generator(100)
        group_order_by_type = {
            QBLeafGroup.Type.MATRIX_1D: 100,
            QBLeafGroup.Type.MATRIX_2D: 200,
        }
        for _type, *categories in group_categories:
            # Group
            group = QBLeafGroupFactory.create(
                qbank=qbank,
                type=_type,
                category_1=categories[0],
                category_2=categories[1],
                category_3=categories[2],
                category_4=categories[3],
                order=group_order_by_type[_type],
                hide_in_framework=QBLeafGroup.check_if_hidden_in_framework(
                    _type,
                    *categories,
                ),
            )
            group_order_by_type[_type] += 1
            # Questions
            question_params = {
                'type': QBQuestion.Type.INTEGER,
                'qbank': qbank,
                'leaf_group': group,
            }
            # Without choices
            QBQuestionFactory.create_batch(random.randrange(4, 10), **question_params)
            # With choices
            QBQuestionFactory.create_batch(
                random.randrange(1, 3),
                **question_params,
                choice_collection=choice_collection_2,
            )
            QBQuestionFactory.create_batch(
                random.randrange(1, 4),
                **question_params,
                choice_collection=choice_collection_1,
            )

    def process_questionnare(self, project, user):
        for qbank in QuestionBank.objects.all():
            questionnaire = QuestionnaireFactory.create(
                qbank=qbank,
                project=project,
                created_by=user,
                modified_by=user,
            )
            QuestionLeafGroup.clone_from_qbank(
                questionnaire,
                questionnaire.created_by,
            )

    def process_project(
        self,
        user: User,
        project: Project,
        role: ProjectMembership.Role,
    ):
        self.stdout.write(f' - Adding user as {role.label}')
        project.add_member(user, role=ProjectMembership.Role.ADMIN)
        self.stdout.write(' - Addding some questionnaire using Dummy QuestionBank')
        self.process_questionnare(project, user)

    @transaction.atomic
    def handle(self, **kwargs):
        if not (settings.DEBUG and settings.ALLOW_DUMMY_DATA_SCRIPT):
            self.stdout.write(
                self.style.ERROR(
                    'You need to enable DEBUG & ALLOW_DUMMY_DATA_SCRIPT to use this'
                )
            )
            return

        user = self.get_or_create_superuser()  # Main user
        self.user_resource_params = {
            'created_by': user,
            'modified_by': user,
        }
        if not User.objects.exclude(pk=user.pk).exists():
            UserFactory.create_batch(10)  # Other users

        if kwargs.get('DELETE_ALL', False):
            self.stdout.write(self.style.WARNING('Removing existing Data'))
            QBQuestion.objects.all().delete()
            Project.objects.all().delete()

        projects = ProjectFactory.create_batch(10, **self.user_resource_params)
        total_projects = len(projects)
        self.stdout.write(f'Created {total_projects} projects')

        # Create Qbanks
        qbanks = QuestionBankFactory.create_batch(3, **self.user_resource_params)
        self.stdout.write(f' - Created qbanks {len(qbanks)}')
        for qbank in qbanks:
            self.stdout.write(f'  - Processing qbank {qbank}')
            self.process_qbank(qbank)

        index = 0
        for projects, role in [
            (projects[:3], ProjectMembership.Role.ADMIN),
            (projects[3:5], ProjectMembership.Role.ADMIN),
            (projects[5:10], ProjectMembership.Role.VIEWER),
        ]:
            for project in projects:
                index += 1
                self.stdout.write(f'- Processing project ({index}/{total_projects}): {project}')
                self.process_project(
                    user,
                    project,
                    role,
                )

        self.stdout.write(
            self.style.SUCCESS('Loaded successfully')
        )
