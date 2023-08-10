from django.core.management.base import BaseCommand
from django.db import transaction

from apps.user.models import User
from apps.user.factories import UserFactory
from apps.project.models import Project, ProjectMembership
from apps.project.factories import ProjectFactory
from apps.questionnaire.models import Question
from apps.questionnaire.factories import (
    QuestionnaireFactory,
    QuestionGroupFactory,
    QuestionFactory,
    ChoiceCollectionFactory,
    ChoiceFactory,
)


class Command(BaseCommand):
    help = 'Load dummy data'

    def create_superuser(self):
        user = UserFactory.create(
            email='admin@test.com',
            password_text='admin123',
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=('is_staff', 'is_superuser'))
        self.stdout.write(f'Added user with credentials: {user.email}:{user.password_text}')
        return user

    def process_questionnare(self, questionnaire):
        # Groups
        group1, group2, _ = QuestionGroupFactory.create_batch(
            3,
            **self.user_resource_params,
            questionnaire=questionnaire,
        )
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
        # -- No group
        question_params = {
            **self.user_resource_params,
            'type': Question.Type.INTEGER,
            'questionnaire': questionnaire,
        }
        QuestionFactory.create_batch(5, **question_params)
        # -- Group 1
        QuestionFactory.create_batch(3, **question_params, group=group1)
        # -- Group 2
        QuestionFactory.create_batch(2, **question_params, group=group2, choice_collection=choice_collection_1)
        QuestionFactory.create_batch(2, **question_params, group=group2, choice_collection=choice_collection_2)

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
            self.process_questionnare(questionnaire)

    @transaction.atomic
    def handle(self, **_):
        user = self.create_superuser()  # Main user
        UserFactory.create_batch(10)  # Other users
        self.user_resource_params = {
            'created_by': user,
            'modified_by': user,
        }
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

        # raise Exception('NOOOP')
        self.stdout.write(
            self.style.SUCCESS('Loaded sucessfully')
        )
