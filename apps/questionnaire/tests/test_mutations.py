from main.tests import TestCase

from apps.project.models import ProjectMembership
from apps.project.factories import ProjectFactory
from apps.questionnaire.models import (
    Questionnaire,
    Question,
    QuestionGroup,
    ChoiceCollection,
)
from apps.user.factories import UserFactory
from apps.questionnaire.factories import (
    QuestionnaireFactory,
    QuestionFactory,
    QuestionGroupFactory,
    ChoiceCollectionFactory,
)


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
            'projectID': self.gID(project.pk),
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
            'projectID': self.gID(project.pk),
            'questionnaireID': self.gID(q1.pk),
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
        variables['questionnaireID'] = self.gID(q2.id)
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
            'projectID': self.gID(project.pk),
            'questionnaireID': self.gID(q1.pk),
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
        variables['questionnaireID'] = self.gID(q2.id)
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
            'projectID': self.gID(project.pk),
            'data': {
                'name': 'question_01',
                'label': 'Question 1',
                'questionnaire': self.gID(q2.pk),
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
        variables['data']['questionnaire'] = self.gID(q1.pk)
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
            'projectID': self.gID(project.pk),
            'questionID': self.gID(question12.pk),
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
        variables['data']['questionnaire'] = self.gID(q2.pk)
        content = self.query_check(
            self.Mutation.QuestionUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestion']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- Another project question
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['questionID'] = self.gID(question2.id)
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
            'projectID': self.gID(project.pk),
            'questionID': self.gID(question1.pk),
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
        variables['questionID'] = self.gID(question2.id)
        content = self.query_check(
            self.Mutation.QuestionDelete,
            variables=variables,
            assert_errors=True,
        )


class TestQuestionTypeMutation(TestCase):
    class Mutation:
        QuestionCreate = TestQuestionMutation.Mutation.QuestionCreate
        QuestionUpdate = TestQuestionMutation.Mutation.QuestionUpdate
        QuestionDelete = TestQuestionMutation.Mutation.QuestionDelete

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.ur_params = dict(created_by=cls.user, modified_by=cls.user)
        # Create some projects
        cls.project = ProjectFactory.create(**cls.ur_params)
        cls.q1 = QuestionnaireFactory.create(**cls.ur_params, project=cls.project)
        cls.project.add_member(cls.user, role=ProjectMembership.Role.MEMBER)
        cls.choice_collection = ChoiceCollectionFactory.create(**cls.ur_params, questionnaire=cls.q1)

    def test_question_choices_types(self):
        # Without login
        variables = {
            'projectID': self.gID(self.project.pk),
            'data': {
                'name': 'question_01',
                'label': 'Question 1',
                'questionnaire': self.gID(self.q1.pk),
                'type': self.genum(Question.Type.SELECT_ONE),
            },
        }

        self.force_login(self.user)

        def _query_check():
            return self.query_check(
                self.Mutation.QuestionCreate,
                variables=variables,
            )['data']['private']['projectScope']['createQuestion']

        # -- Without choices
        content = _query_check()
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        # -- With choices
        variables['data']['choiceCollection'] = self.gID(self.choice_collection.pk)
        content = _query_check()
        assert content['ok'] is True, content
        assert content['errors'] is None, content
        assert content['result']['name'] == variables['data']['name'], content
        assert content['result']['label'] == variables['data']['label'], content


class TestQuestionGroupMutation(TestCase):
    class Mutation:
        QuestionGroupCreate = '''
            mutation MyMutation($projectID: ID!, $data: QuestionGroupCreateInput!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  createQuestionGroup(data: $data) {
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

        QuestionGroupUpdate = '''
            mutation MyMutation($projectID: ID!, $questionGroupID: ID!, $data: QuestionGroupUpdateInput!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  updateQuestionGroup(id: $questionGroupID, data: $data) {
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

        QuestionGroupDelete = '''
            mutation MyMutation($projectID: ID!, $questionGroupID: ID!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  deleteQuestionGroup(id: $questionGroupID) {
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

    def test_create_question_group(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        question_group_count = QuestionGroup.objects.count()
        # Without login
        variables = {
            'projectID': self.gID(project.pk),
            'data': {
                'name': 'question_group_01',
                'label': 'Question Group 1',
                'relevant': 'Not relevant',
                'questionnaire': self.gID(q2.pk),
            },
        }
        content = self.query_check(self.Mutation.QuestionGroupCreate, variables=variables, assert_errors=True)
        assert content['data'] is None
        # No change
        assert QuestionGroup.objects.count() == question_group_count

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionGroupCreate, variables=variables)
        assert content['data']['private']['projectScope'] is None
        # No change
        assert QuestionGroup.objects.count() == question_group_count

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionGroupCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestionGroup']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        # No change
        assert QuestionGroup.objects.count() == question_group_count

        # -- With membership - With write access
        # -- Invalid questionnaire id
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionGroupCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestionGroup']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        # -- Valid questionnaire id
        variables['data']['questionnaire'] = self.gID(q1.pk)
        content = self.query_check(
            self.Mutation.QuestionGroupCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestionGroup']
        assert content['ok'] is True, content
        assert content['errors'] is None, content
        assert content['result']['name'] == variables['data']['name'], content
        assert content['result']['label'] == variables['data']['label'], content
        # 1 new
        assert QuestionGroup.objects.count() == question_group_count + 1
        # -- Simple name unique validation
        content = self.query_check(
            self.Mutation.QuestionGroupCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestionGroup']
        assert content['ok'] is not True, content
        assert content['errors'] is not None, content
        # Same as last
        assert QuestionGroup.objects.count() == question_group_count + 1

    def test_update_question_group(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        QuestionGroupFactory.create(**ur_params, questionnaire=q1, name='question_group_01')
        question_group_12 = QuestionGroupFactory.create(**ur_params, questionnaire=q1, name='question_group_02')
        question_group_2 = QuestionGroupFactory.create(**ur_params, questionnaire=q2, name='question_group_01')

        # Without login
        variables = {
            'projectID': self.gID(project.pk),
            'questionGroupID': self.gID(question_group_12.pk),
            'data': {
                'name': 'question_group_002',
                'label': 'QuestionGroup 2',
            },
        }
        content = self.query_check(self.Mutation.QuestionGroupUpdate, variables=variables, assert_errors=True)
        assert content['data'] is None

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionGroupUpdate, variables=variables)
        assert content['data']['private']['projectScope'] is None

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionGroupUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestionGroup']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- With membership - With write access
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionGroupUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestionGroup']
        assert content['ok'] is True, content
        assert content['errors'] is None, content
        assert content['result']['name'] == variables['data']['name'], content
        assert content['result']['label'] == variables['data']['label'], content

        # -- Using another question name
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['data']['name'] = 'question_group_01'
        content = self.query_check(
            self.Mutation.QuestionGroupUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestionGroup']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        variables['data']['name'] = 'question_group_02'

        # -- Using another project questionnaire name
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['data']['questionnaire'] = self.gID(q2.pk)
        content = self.query_check(
            self.Mutation.QuestionGroupUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestionGroup']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- Another project question
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['questionGroupID'] = self.gID(question_group_2.id)
        content = self.query_check(
            self.Mutation.QuestionGroupUpdate,
            variables=variables,
            assert_errors=True,
        )

    def test_delete_question_group(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        question1 = QuestionGroupFactory.create(**ur_params, questionnaire=q1, name='question_group_0101')
        question_group_2 = QuestionGroupFactory.create(**ur_params, questionnaire=q2, name='question_group_0201')

        # Without login
        variables = {
            'projectID': self.gID(project.pk),
            'questionGroupID': self.gID(question1.pk),
        }
        content = self.query_check(self.Mutation.QuestionGroupDelete, variables=variables, assert_errors=True)
        assert content['data'] is None

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionGroupDelete, variables=variables)
        assert content['data']['private']['projectScope'] is None

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionGroupDelete,
            variables=variables,
        )['data']['private']['projectScope']['deleteQuestionGroup']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- With membership - With write access
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionGroupDelete,
            variables=variables,
        )['data']['private']['projectScope']['deleteQuestionGroup']
        assert content['ok'] is True, content
        assert content['errors'] is None, content

        # -- Another project question
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['questionGroupID'] = self.gID(question_group_2.id)
        content = self.query_check(
            self.Mutation.QuestionGroupDelete,
            variables=variables,
            assert_errors=True,
        )


class TestChoiceCollectionMutation(TestCase):
    class Mutation:
        ChoiceCollectionCreate = '''
            mutation MyMutation($projectID: ID!, $data: QuestionChoiceCollectionCreateInput!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  createQuestionChoiceCollection(data: $data) {
                    ok
                    errors
                    result {
                      id
                      name
                      label
                      choices {
                        id
                        clientId
                        label
                        name
                        collectionId
                      }
                    }
                  }
                }
              }
            }
        '''

        ChoiceCollectionUpdate = '''
            mutation MyMutation($projectID: ID!, $questionGroupID: ID!, $data: QuestionChoiceCollectionUpdateInput!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  updateQuestionChoiceCollection(id: $questionGroupID, data: $data) {
                    ok
                    errors
                    result {
                      id
                      name
                      label
                      choices {
                        id
                        clientId
                        label
                        name
                        collectionId
                      }
                    }
                  }
                }
              }
            }
        '''

        ChoiceCollectionDelete = '''
            mutation MyMutation($projectID: ID!, $questionGroupID: ID!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  deleteQuestionChoiceCollection(id: $questionGroupID) {
                    ok
                    errors
                    result {
                      id
                      name
                      label
                      choices {
                        id
                        clientId
                        label
                        name
                        collectionId
                      }
                    }
                  }
                }
              }
            }
        '''

    def test_create_choice_collection(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        choice_collection_count = ChoiceCollection.objects.count()
        # Without login
        variables = {
            'projectID': self.gID(project.pk),
            'data': {
                'name': 'choice_collection_01',
                'label': 'Question Group 1',
                'questionnaire': self.gID(q2.pk),
                'choices': [
                    {
                        'clientId': 'choice-1',
                        'name': 'choice-1',
                        'label': 'Choice 1',
                    },
                    {
                        'clientId': 'choice-2',
                        'name': 'choice-2',
                        'label': 'Choice 2',
                    }
                ],
            },
        }
        content = self.query_check(self.Mutation.ChoiceCollectionCreate, variables=variables, assert_errors=True)
        assert content['data'] is None
        # No change
        assert ChoiceCollection.objects.count() == choice_collection_count

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.ChoiceCollectionCreate, variables=variables)
        assert content['data']['private']['projectScope'] is None
        # No change
        assert ChoiceCollection.objects.count() == choice_collection_count

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.ChoiceCollectionCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestionChoiceCollection']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        # No change
        assert ChoiceCollection.objects.count() == choice_collection_count

        # -- With membership - With write access
        # -- Invalid questionnaire id
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.ChoiceCollectionCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestionChoiceCollection']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        # -- Valid questionnaire id
        variables['data']['questionnaire'] = self.gID(q1.pk)
        content = self.query_check(
            self.Mutation.ChoiceCollectionCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestionChoiceCollection']
        assert content['ok'] is True, content
        assert content['errors'] is None, content
        assert content['result']['name'] == variables['data']['name'], content
        assert content['result']['label'] == variables['data']['label'], content
        self.assertListDictEqual(
            content['result']['choices'],
            [
                {
                    **choice,
                    'collectionId': content['result']['id']
                }
                for choice in variables['data']['choices']
            ],
            content,
            ignore_keys={'id'},
        )
        # 1 new
        assert ChoiceCollection.objects.count() == choice_collection_count + 1
        # -- Simple name unique validation
        content = self.query_check(
            self.Mutation.ChoiceCollectionCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestionChoiceCollection']
        assert content['ok'] is not True, content
        assert content['errors'] is not None, content
        # Same as last
        assert ChoiceCollection.objects.count() == choice_collection_count + 1

    def test_update_choice_collection(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        ChoiceCollectionFactory.create(**ur_params, questionnaire=q1, name='choice_collection_01')
        choice_collection_12 = ChoiceCollectionFactory.create(**ur_params, questionnaire=q1, name='choice_collection_02')
        choice_collection_2 = ChoiceCollectionFactory.create(**ur_params, questionnaire=q2, name='choice_collection_01')

        # Without login
        variables = {
            'projectID': self.gID(project.pk),
            'questionGroupID': self.gID(choice_collection_12.pk),
            'data': {
                'name': 'choice_collection_002',
                'label': 'ChoiceCollection 2',
            },
        }
        content = self.query_check(self.Mutation.ChoiceCollectionUpdate, variables=variables, assert_errors=True)
        assert content['data'] is None

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.ChoiceCollectionUpdate, variables=variables)
        assert content['data']['private']['projectScope'] is None

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.ChoiceCollectionUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestionChoiceCollection']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- With membership - With write access
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.ChoiceCollectionUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestionChoiceCollection']
        assert content['ok'] is True, content
        assert content['errors'] is None, content
        assert content['result']['name'] == variables['data']['name'], content
        assert content['result']['label'] == variables['data']['label'], content

        # -- Using another question name
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['data']['name'] = 'choice_collection_01'
        content = self.query_check(
            self.Mutation.ChoiceCollectionUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestionChoiceCollection']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        variables['data']['name'] = 'choice_collection_02'

        # -- Using another project questionnaire name
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['data']['questionnaire'] = self.gID(q2.pk)
        content = self.query_check(
            self.Mutation.ChoiceCollectionUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestionChoiceCollection']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- Another project question
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['questionGroupID'] = self.gID(choice_collection_2.id)
        content = self.query_check(
            self.Mutation.ChoiceCollectionUpdate,
            variables=variables,
            assert_errors=True,
        )

    def test_delete_choice_collection(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        question1 = ChoiceCollectionFactory.create(**ur_params, questionnaire=q1, name='choice_collection_0101')
        choice_collection_2 = ChoiceCollectionFactory.create(**ur_params, questionnaire=q2, name='choice_collection_0201')

        # Without login
        variables = {
            'projectID': self.gID(project.pk),
            'questionGroupID': self.gID(question1.pk),
        }
        content = self.query_check(self.Mutation.ChoiceCollectionDelete, variables=variables, assert_errors=True)
        assert content['data'] is None

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.ChoiceCollectionDelete, variables=variables)
        assert content['data']['private']['projectScope'] is None

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.ChoiceCollectionDelete,
            variables=variables,
        )['data']['private']['projectScope']['deleteQuestionChoiceCollection']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- With membership - With write access
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.ChoiceCollectionDelete,
            variables=variables,
        )['data']['private']['projectScope']['deleteQuestionChoiceCollection']
        assert content['ok'] is True, content
        assert content['errors'] is None, content

        # -- Another project question
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['questionGroupID'] = self.gID(choice_collection_2.id)
        content = self.query_check(
            self.Mutation.ChoiceCollectionDelete,
            variables=variables,
            assert_errors=True,
        )
