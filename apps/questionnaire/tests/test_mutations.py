from main.tests import TestCase

from apps.project.models import ProjectMembership
from apps.project.factories import ProjectFactory
from apps.questionnaire.enums import QuestionLeafGroupVisibilityActionEnum
from apps.questionnaire.models import (
    Questionnaire,
    Question,
    QuestionLeafGroup,
    ChoiceCollection,
)
from apps.user.factories import UserFactory
from apps.questionnaire.factories import (
    QuestionnaireFactory,
    QuestionFactory,
    QuestionLeafGroupFactory,
    ChoiceCollectionFactory,
)


class TestQuestionnaireMutation(TestCase):
    class Mutation:
        QuestionnaireCreate = '''
            mutation MyMutation($projectId: ID!, $data: QuestionnaireCreateInput!) {
              private {
                id
                projectScope(pk: $projectId) {
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
            mutation MyMutation($projectId: ID!, $questionnaireId: ID!, $data: QuestionnaireUpdateInput!) {
              private {
                id
                projectScope(pk: $projectId) {
                  id
                  updateQuestionnaire(id: $questionnaireId, data: $data) {
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
            mutation MyMutation($projectId: ID!, $questionnaireId: ID!) {
              private {
                id
                projectScope(pk: $projectId) {
                  id
                  deleteQuestionnaire(id: $questionnaireId) {
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
            'projectId': self.gID(project.pk),
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
            'projectId': self.gID(project.pk),
            'questionnaireId': self.gID(q1.pk),
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
        variables['questionnaireId'] = self.gID(q2.id)
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
        q1, q1_2 = QuestionnaireFactory.create_batch(2, **ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)
        # Create some questions, groups and choice collections
        group1 = QuestionLeafGroupFactory.create(
            **ur_params,
            questionnaire=q1,
            type=QuestionLeafGroup.Type.MATRIX_1D,
            category_1=QuestionLeafGroup.Category1.CONTEXT,
            category_2=QuestionLeafGroup.Category2.POLITICS,
        )
        group1_2 = QuestionLeafGroupFactory.create(
            **ur_params,
            questionnaire=q1_2,
            type=QuestionLeafGroup.Type.MATRIX_1D,
            category_1=QuestionLeafGroup.Category1.CONTEXT,
            category_2=QuestionLeafGroup.Category2.DEMOGRAPHY,
        )
        group2 = QuestionLeafGroupFactory.create(
            **ur_params,
            questionnaire=q2,
            type=QuestionLeafGroup.Type.MATRIX_1D,
            category_1=QuestionLeafGroup.Category1.CONTEXT,
            category_2=QuestionLeafGroup.Category2.POLITICS,
        )
        # -- q1
        choice_collections = ChoiceCollectionFactory.create_batch(3, **ur_params, questionnaire=q1)
        QuestionFactory.create_batch(
            2, **ur_params, questionnaire=q1, leaf_group=group1, choice_collection=choice_collections[0])
        QuestionFactory.create_batch(
            3, **ur_params, questionnaire=q1, leaf_group=group1, choice_collection=choice_collections[1])
        QuestionFactory.create_batch(3, **ur_params, questionnaire=q1, leaf_group=group1)
        QuestionFactory.create_batch(3, **ur_params, questionnaire=q1_2, leaf_group=group1_2)
        # -- q2
        QuestionFactory.create_batch(3, **ur_params, questionnaire=q1, leaf_group=group2)

        # Without login
        variables = {
            'projectId': self.gID(project.pk),
            'questionnaireId': self.gID(q1.pk),
        }
        content = self.query_check(self.Mutation.QuestionnaireDelete, variables=variables, assert_errors=True)
        assert content['data'] is None

        # Current entities counts
        def _get_counts():
            return {
                'questions': Question.objects.count(),
                'choice_collections': ChoiceCollection.objects.count(),
                'groups': QuestionLeafGroup.objects.count(),
                'questionnair': Questionnaire.objects.count(),
            }
        counts = _get_counts()
        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionnaireDelete, variables=variables)
        assert content['data']['private']['projectScope'] is None
        assert counts == _get_counts()

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionnaireDelete,
            variables=variables,
        )['data']['private']['projectScope']['deleteQuestionnaire']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        assert counts == _get_counts()

        # -- With membership - With write access
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionnaireDelete,
            variables=variables,
        )['data']['private']['projectScope']['deleteQuestionnaire']
        assert content['ok'] is True, content
        assert content['errors'] is None, content
        counts['questions'] -= 11
        counts['choice_collections'] -= 3
        counts['questionnair'] -= 1
        counts['groups'] -= 1
        assert counts == _get_counts()

        # -- Another questionnaire
        variables['questionnaireId'] = self.gID(q1_2.id)
        content = self.query_check(
            self.Mutation.QuestionnaireDelete,
            variables=variables,
        )['data']['private']['projectScope']['deleteQuestionnaire']
        assert content['ok'] is True, content
        assert content['errors'] is None, content
        counts['questions'] -= 3
        counts['questionnair'] -= 1
        counts['groups'] -= 1
        assert counts == _get_counts()

        # -- Another project questionnaire
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        variables['questionnaireId'] = self.gID(q2.id)
        content = self.query_check(
            self.Mutation.QuestionnaireDelete,
            variables=variables,
            assert_errors=True,
        )
        assert counts == _get_counts()


class TestQuestionMutation(TestCase):
    class Mutation:
        QuestionCreate = '''
            mutation MyMutation($projectId: ID!, $data: QuestionCreateInput!) {
              private {
                id
                projectScope(pk: $projectId) {
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
            mutation MyMutation($projectId: ID!, $questionID: ID!, $data: QuestionUpdateInput!) {
              private {
                id
                projectScope(pk: $projectId) {
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
            mutation MyMutation($projectId: ID!, $questionID: ID!) {
              private {
                id
                projectScope(pk: $projectId) {
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

        [q1_group] = QuestionLeafGroupFactory.static_generator(1, **ur_params, questionnaire=q1)
        [q2_group] = QuestionLeafGroupFactory.static_generator(1, **ur_params, questionnaire=q2)

        question_count = Question.objects.count()
        # Without login
        variables = {
            'projectId': self.gID(project.pk),
            'data': {
                'name': 'question_01',
                'label': 'Question 1',
                'questionnaire': self.gID(q2.pk),
                'leafGroup': self.gID(q2_group.pk),
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
        # -- Invalid leaf group
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionCreate,
            variables=variables,
        )['data']['private']['projectScope']['createQuestion']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content
        # -- Valid questionnaire id & leaf group
        variables['data']['leafGroup'] = self.gID(q1_group.pk)
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

        [group1] = QuestionLeafGroupFactory.static_generator(1, **ur_params, questionnaire=q1)
        [group2] = QuestionLeafGroupFactory.static_generator(1, **ur_params, questionnaire=q2)

        question_params = {**ur_params, 'type': Question.Type.INTEGER}
        QuestionFactory.create(**question_params, questionnaire=q1, name='question_01', leaf_group=group1)
        question12 = QuestionFactory.create(**question_params, questionnaire=q1, leaf_group=group1, name='question_02')
        question2 = QuestionFactory.create(**question_params, questionnaire=q2, leaf_group=group2, name='question_01')

        # Without login
        variables = {
            'projectId': self.gID(project.pk),
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

        [group1] = QuestionLeafGroupFactory.static_generator(1, **ur_params, questionnaire=q1)
        [group2] = QuestionLeafGroupFactory.static_generator(1, **ur_params, questionnaire=q2)

        question_params = {**ur_params, 'type': Question.Type.INTEGER}
        question1 = QuestionFactory.create(**question_params, questionnaire=q1, name='question_0101', leaf_group=group1)
        question2 = QuestionFactory.create(**question_params, questionnaire=q2, name='question_0201', leaf_group=group2)

        # Without login
        variables = {
            'projectId': self.gID(project.pk),
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
        [group1] = QuestionLeafGroupFactory.static_generator(1, **self.ur_params, questionnaire=self.q1)

        # Without login
        variables = {
            'projectId': self.gID(self.project.pk),
            'data': {
                'name': 'question_01',
                'label': 'Question 1',
                'questionnaire': self.gID(self.q1.pk),
                'type': self.genum(Question.Type.SELECT_ONE),
                'leafGroup': self.gID(group1.pk),
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
        QuestionLeafGroupVisiblityUpdate = '''
            mutation MyMutation(
                $projectId: ID!,
                $questionLeafGroupID: ID!,
                $visibility: QuestionLeafGroupVisibilityActionEnum!
            ) {
              private {
                id
                projectScope(pk: $projectId) {
                  id
                  updateQuestionGroupLeafVisibility(id: $questionLeafGroupID, visibility: $visibility) {
                    ok
                    errors
                    result {
                      id
                      name
                      isHidden
                    }
                  }
                }
              }
            }
        '''

        QuestionLeafGroupOrderBulkUpdate = '''
            mutation MyMutation(
                $projectId: ID!,
                $questionnairId: ID!,
                $data: [QuestionLeafGroupOrderInputType!]!
            ) {
              private {
                id
                projectScope(pk: $projectId) {
                  id
                  bulkUpdateQuestionnairQuestionGroupsLeafOrder(questionnaireId: $questionnairId, data: $data) {
                    errors
                    results {
                      id
                      name
                      order
                    }
                  }
                }
              }
            }
        '''

    def test_question_leaf_group_visibility(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1 = QuestionnaireFactory.create(**ur_params, project=project)
        q2 = QuestionnaireFactory.create(**ur_params, project=project2)

        [group1] = QuestionLeafGroupFactory.static_generator(1, **ur_params, questionnaire=q1)
        [group2] = QuestionLeafGroupFactory.static_generator(1, **ur_params, questionnaire=q2)

        # Without login
        variables = {
            'projectId': self.gID(project.pk),
            'questionLeafGroupID': self.gID(group2.pk),
            'visibility': self.genum(QuestionLeafGroupVisibilityActionEnum.HIDE),
        }
        content = self.query_check(self.Mutation.QuestionLeafGroupVisiblityUpdate, variables=variables, assert_errors=True)
        assert content['data'] is None

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionLeafGroupVisiblityUpdate, variables=variables)
        assert content['data']['private']['projectScope'] is None

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionLeafGroupVisiblityUpdate,
            variables=variables,
        )['data']['private']['projectScope']['updateQuestionGroupLeafVisibility']
        assert content['ok'] is False, content
        assert content['errors'] is not None, content

        # -- With membership - With write access
        # -- Invalid question leaf group id
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(self.Mutation.QuestionLeafGroupVisiblityUpdate, variables=variables, assert_errors=True)

        # -- Valid question leaf group id
        variables['questionLeafGroupID'] = self.gID(group1.pk)
        for visibility, is_hidden_value in [
            (self.genum(QuestionLeafGroupVisibilityActionEnum.HIDE), True),
            (self.genum(QuestionLeafGroupVisibilityActionEnum.SHOW), False),
        ]:
            variables['visibility'] = visibility
            content = self.query_check(
                self.Mutation.QuestionLeafGroupVisiblityUpdate,
                variables=variables,
            )['data']['private']['projectScope']['updateQuestionGroupLeafVisibility']
            group1.refresh_from_db()
            assert content['ok'] is True, content
            assert content['errors'] is None, content
            assert content['result']['id'] == variables['questionLeafGroupID'], content
            assert content['result']['isHidden'] == is_hidden_value, content
            assert group1.is_hidden == is_hidden_value

    def test_question_leaf_group_order_update(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project, project2 = ProjectFactory.create_batch(2, **ur_params)
        q1_1 = QuestionnaireFactory.create(**ur_params, project=project)
        q1_2 = QuestionnaireFactory.create(**ur_params, project=project)
        q2_1 = QuestionnaireFactory.create(**ur_params, project=project2)

        [
            group1_1_1,
            group1_1_2,
            group1_1_3,
            group1_1_4
        ] = QuestionLeafGroupFactory.static_generator(4, **ur_params, questionnaire=q1_1)
        [group1_2_1, group1_2_2] = QuestionLeafGroupFactory.static_generator(2, **ur_params, questionnaire=q1_2)
        [group2_1_1, group2_1_2] = QuestionLeafGroupFactory.static_generator(2, **ur_params, questionnaire=q2_1)

        valid_group_order_set = [
            (group1_1_1, 1001),
            (group1_1_2, 1001),
            (group1_1_3, 1001),
            (group1_1_4, 1001),
        ]
        # Without login
        variables = {
            'projectId': self.gID(project.pk),
            'questionnairId': self.gID(q1_1.pk),
            'data': [
                {
                    'id': self.gID(group.pk),
                    'order': order,
                }
                for group, order in (
                    # Valid groups
                    *valid_group_order_set,
                    # Invalid groups
                    # -- Another questionnair
                    (group1_2_1, 1001),
                    (group1_2_2, 1001),
                    # -- Another questionnair another project
                    (group2_1_1, 1001),
                    (group2_1_2, 1001),
                )
            ]
        }
        content = self.query_check(self.Mutation.QuestionLeafGroupOrderBulkUpdate, variables=variables, assert_errors=True)
        assert content['data'] is None

        # With login
        # -- Without membership
        self.force_login(user)
        content = self.query_check(self.Mutation.QuestionLeafGroupOrderBulkUpdate, variables=variables)
        assert content['data']['private']['projectScope'] is None

        # -- With membership - But read access only
        project.add_member(user, role=ProjectMembership.Role.VIEWER)
        content = self.query_check(
            self.Mutation.QuestionLeafGroupOrderBulkUpdate,
            variables=variables,
        )['data']['private']['projectScope']['bulkUpdateQuestionnairQuestionGroupsLeafOrder']
        assert content['errors'] is not None, content

        # -- With membership - With write access
        project.add_member(user, role=ProjectMembership.Role.MEMBER)
        content = self.query_check(
            self.Mutation.QuestionLeafGroupOrderBulkUpdate,
            variables=variables,
        )['data']['private']['projectScope']['bulkUpdateQuestionnairQuestionGroupsLeafOrder']
        assert content['errors'] is None, content
        assert content['results'] == [
            {
                'id': self.gID(group.pk),
                'name': group.name,
                'order': order,
            }
            for group, order in valid_group_order_set
        ]


class TestChoiceCollectionMutation(TestCase):
    class Mutation:
        ChoiceCollectionCreate = '''
            mutation MyMutation($projectId: ID!, $data: QuestionChoiceCollectionCreateInput!) {
              private {
                id
                projectScope(pk: $projectId) {
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
            mutation MyMutation($projectId: ID!, $questionGroupID: ID!, $data: QuestionChoiceCollectionUpdateInput!) {
              private {
                id
                projectScope(pk: $projectId) {
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
            mutation MyMutation($projectId: ID!, $questionGroupID: ID!) {
              private {
                id
                projectScope(pk: $projectId) {
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
            'projectId': self.gID(project.pk),
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
            'projectId': self.gID(project.pk),
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
            'projectId': self.gID(project.pk),
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
