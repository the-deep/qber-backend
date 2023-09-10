import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from apps.user.models import User
from apps.user.factories import UserFactory
from apps.project.models import Project, ProjectMembership
from apps.project.factories import ProjectFactory
from apps.questionnaire.models import Question, Questionnaire, QuestionLeafGroup
from apps.questionnaire.factories import (
    QuestionnaireFactory,
    QuestionLeafGroupFactory,
    QuestionFactory,
    ChoiceCollectionFactory,
    ChoiceFactory,
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

    def process_questionnaire(self, questionnaire: Questionnaire):
        # Choices
        # -- Collection
        choice_collection_1, choice_collection_2, choice_collection_3 = ChoiceCollectionFactory.create_batch(
            3,
            **self.user_resource_params,
            questionnaire=questionnaire,
        )
        # -- Choices
        ChoiceFactory.create_batch(10, collection=choice_collection_1)
        ChoiceFactory.create_batch(5, collection=choice_collection_2)
        ChoiceFactory.create_batch(7, collection=choice_collection_3)

        # Questions
        group_categories = QuestionLeafGroupFactory.random_category_generator(100)
        group_order_by_type = {
            QuestionLeafGroup.Type.MATRIX_1D: 100,
            QuestionLeafGroup.Type.MATRIX_2D: 200,
        }
        for _type, *categories in group_categories:
            # Group
            group = QuestionLeafGroupFactory.create(
                questionnaire=questionnaire,
                type=_type,
                category_1=categories[0],
                category_2=categories[1],
                category_3=categories[2],
                category_4=categories[3],
                order=group_order_by_type[_type],
                **self.user_resource_params,
            )
            group_order_by_type[_type] += 1
            # Questions
            question_params = {
                **self.user_resource_params,
                'type': Question.Type.INTEGER,
                'questionnaire': questionnaire,
                'leaf_group': group,
            }
            # Without choices
            QuestionFactory.create_batch(random.randrange(4, 10), **question_params)
            # With choices
            QuestionFactory.create_batch(random.randrange(1, 3), **question_params, choice_collection=choice_collection_2)
            QuestionFactory.create_batch(random.randrange(1, 4), **question_params, choice_collection=choice_collection_1)

    def process_project(
        self,
        user: User,
        project: Project,
        role: ProjectMembership.Role,
    ):
        self.stdout.write(f' - Adding user as {role.label}')
        project.add_member(user, role=ProjectMembership.Role.ADMIN)
        # Create Questionnaires
        questionnaires = QuestionnaireFactory.create_batch(3, project=project, **self.user_resource_params)
        self.stdout.write(f' - Created questionnaires {len(questionnaires)}')
        for questionnaire in questionnaires:
            self.stdout.write(f'  - Processing questionnaire {questionnaire}')
            self.process_questionnaire(questionnaire)

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
            Question.objects.all().delete()
            Project.objects.all().delete()

        projects = ProjectFactory.create_batch(10, **self.user_resource_params)
        total_projects = len(projects)
        self.stdout.write(f'Created {total_projects} projects')

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
            self.style.SUCCESS('Loaded sucessfully')
        )
