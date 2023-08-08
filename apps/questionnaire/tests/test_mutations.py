from main.tests import TestCase

from apps.project.models import ProjectMembership
from apps.project.factories import ProjectFactory
from apps.questionnaire.models import Questionnaire, Question
from apps.user.factories import UserFactory
from apps.questionnaire.factories import QuestionnaireFactory, QuestionFactory


class TestQuestionnaireMutation(TestCase):
    class Mutation:
        QuestionnaireCreate = '''
            mutation MyMutation($projectID: ID!, $data: QuestionnaireCreateInput!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  createQuestionnaire(data: $data) {
                    ok
                    errors
                    result {
                      id
                      title
                    }
                  }
                }
              }
            }
        '''

        QuestionnaireUpdate = '''
            mutation MyMutation($projectID: ID!, $questionnaireID: ID!, $data: QuestionnaireUpdateInput!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  updateQuestionnaire(id: $questionnaireID, data: $data) {
                    ok
                    errors
                    result {
                      id
                      title
                    }
                  }
                }
              }
            }
        '''

        QuestionnaireDelete = '''
            mutation MyMutation($projectID: ID!, $questionnaireID: ID!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  deleteQuestionnaire(id: $questionnaireID) {
                    ok
                    errors
                    result {
                      id
                      title
                    }
                  }
                }
              }
            }
        '''

    def test_create_questionnaire(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project = ProjectFactory.create(**ur_params)

        questionnaire_count = Questionnaire.objects.count()
        # Without login
        variables = {
            'projectID': str(project.pk),
            'data': {'title': 'Questionnaire 1'},
        }
        content = self.query_check(self.Mutation.QuestionnaireCreate, variables=variables, assert_errors=True)
        assert content['data'] is None
        # No change
        assert Questionnaire.objects.count() == questionnaire_count

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionnaireCreate, variables=variables)
        assert content['data']['private']['projectScope'] is None
        # No change
        assert Questionnaire.objects.count() == questionnaire_count

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionnaireCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestionnaire']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        # No change
        assert Questionnaire.objects.count() == questionnaire_count

        # -- With membership - With write access
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionnaireCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestionnaire']
        assert content['ok'] is True, content
        assert content['errors'] is None, content
        assert content['result']['title'] == variables['data']['title'], content
        # 1 new
        assert Questionnaire.objects.count() == questionnaire_count + 1

    def test_update_questionnaire(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        # Without login
        variables = {
            'projectID': str(project.pk),
            'questionnaireID': str(q1.pk),
            'data': {'title': 'Questionnaire 1'},
        }
        content = self.query_check(self.Mutation.QuestionnaireUpdate, variables=variables, assert_errors=True)
        assert content['data'] is None

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionnaireUpdate, variables=variables)
        assert content['data']['private']['projectScope'] is None

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionnaireUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestionnaire']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- With membership - With write access
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionnaireUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestionnaire']
        assert content['ok'] is True, content
        assert content['errors'] is None, content
        assert content['result']['title'] == variables['data']['title'], content

        # -- Another project questionnaire
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['questionnaireID'] = str(q2.id)
        content = self.query_check(
            self.Mutation.QuestionnaireUpdate,
            variables=variables,
            assert_errors=True,
        )

    def test_delete_questionnaire(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        # Without login
        variables = {
            'projectID': str(project.pk),
            'questionnaireID': str(q1.pk),
        }
        content = self.query_check(self.Mutation.QuestionnaireDelete, variables=variables, assert_errors=True)
        assert content['data'] is None

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionnaireDelete, variables=variables)
        assert content['data']['private']['projectScope'] is None

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionnaireDelete,
            variables=variables,
        )['data']['private']['projectScope']['deleteQuestionnaire']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- With membership - With write access
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionnaireDelete,
            variables=variables,
        )['data']['private']['projectScope']['deleteQuestionnaire']
        assert content['ok'] is True, content
        assert content['errors'] is None, content

        # -- Another project questionnaire
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['questionnaireID'] = str(q2.id)
        content = self.query_check(
            self.Mutation.QuestionnaireDelete,
            variables=variables,
            assert_errors=True,
        )


class TestQuestionMutation(TestCase):
    class Mutation:
        QuestionCreate = '''
            mutation MyMutation($projectID: ID!, $data: QuestionCreateInput!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  createQuestion(data: $data) {
                    ok
                    errors
                    result {
                      id
                      name
                      label
                    }
                  }
                }
              }
            }
        '''

        QuestionUpdate = '''
            mutation MyMutation($projectID: ID!, $questionID: ID!, $data: QuestionUpdateInput!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  updateQuestion(id: $questionID, data: $data) {
                    ok
                    errors
                    result {
                      id
                      name
                      label
                    }
                  }
                }
              }
            }
        '''

        QuestionDelete = '''
            mutation MyMutation($projectID: ID!, $questionID: ID!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  deleteQuestion(id: $questionID) {
                    ok
                    errors
                    result {
                      id
                      name
                      label
                    }
                  }
                }
              }
            }
        '''

    def test_create_question(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        question_count = Question.objects.count()
        # Without login
        variables = {
            'projectID': str(project.pk),
            'data': {
                'name': 'question_01',
                'label': 'Question 1',
                'questionnaire': str(q2.pk),
                'type': self.genum(Question.Type.INTEGER),
            },
        }
        content = self.query_check(self.Mutation.QuestionCreate, variables=variables, assert_errors=True)
        assert content['data'] is None
        # No change
        assert Question.objects.count() == question_count

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionCreate, variables=variables)
        assert content['data']['private']['projectScope'] is None
        # No change
        assert Question.objects.count() == question_count

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestion']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        # No change
        assert Question.objects.count() == question_count

        # -- With membership - With write access
        # -- Invalid questionnaire id
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestion']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        # -- Valid questionnaire id
        variables['data']['questionnaire'] = str(q1.pk)
        content = self.query_check(
            self.Mutation.QuestionCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestion']
        assert content['ok'] is True, content
        assert content['errors'] is None, content
        assert content['result']['name'] == variables['data']['name'], content
        assert content['result']['label'] == variables['data']['label'], content
        # 1 new
        assert Question.objects.count() == question_count + 1
        # -- Simple name unique validation
        content = self.query_check(
            self.Mutation.QuestionCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestion']
        assert content['ok'] is not True, content
        assert content['errors'] is not None, content
        # Same as last
        assert Question.objects.count() == question_count + 1

    def test_update_question(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        question_params = {**ur_params, 'type': Question.Type.INTEGER}
        QuestionFactory.create(**question_params, questionnaire=q1, name='question_01')
        question12 = QuestionFactory.create(**question_params, questionnaire=q1, name='question_02')
        question2 = QuestionFactory.create(**question_params, questionnaire=q2, name='question_01')

        # Without login
        variables = {
            'projectID': str(project.pk),
            'questionID': str(question12.pk),
            'data': {
                'name': 'question_002',
                'label': 'Question 2',
            },
        }
        content = self.query_check(self.Mutation.QuestionUpdate, variables=variables, assert_errors=True)
        assert content['data'] is None

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionUpdate, variables=variables)
        assert content['data']['private']['projectScope'] is None

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestion']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- With membership - With write access
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestion']
        assert content['ok'] is True, content
        assert content['errors'] is None, content
        assert content['result']['name'] == variables['data']['name'], content
        assert content['result']['label'] == variables['data']['label'], content

        # -- Using another question name
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['data']['name'] = 'question_01'
        content = self.query_check(
            self.Mutation.QuestionUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestion']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        variables['data']['name'] = 'question_02'

        # -- Using another project questionnaire name
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['data']['questionnaire'] = str(q2.pk)
        content = self.query_check(
            self.Mutation.QuestionUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestion']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- Another project question
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['questionID'] = str(question2.id)
        content = self.query_check(
            self.Mutation.QuestionUpdate,
            variables=variables,
            assert_errors=True,
        )

    def test_delete_question(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        question_params = {**ur_params, 'type': Question.Type.INTEGER}
        question1 = QuestionFactory.create(**question_params, questionnaire=q1, name='question_0101')
        question2 = QuestionFactory.create(**question_params, questionnaire=q2, name='question_0201')

        # Without login
        variables = {
            'projectID': str(project.pk),
            'questionID': str(question1.pk),
        }
        content = self.query_check(self.Mutation.QuestionDelete, variables=variables, assert_errors=True)
        assert content['data'] is None

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionDelete, variables=variables)
        assert content['data']['private']['projectScope'] is None

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionDelete,
            variables=variables,
        )['data']['private']['projectScope']['deleteQuestion']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- With membership - With write access
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionDelete,
            variables=variables,
        )['data']['private']['projectScope']['deleteQuestion']
        assert content['ok'] is True, content
        assert content['errors'] is None, content

        # -- Another project question
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['questionID'] = str(question2.id)
        content = self.query_check(
            self.Mutation.QuestionDelete,
            variables=variables,
            assert_errors=True,
        )
