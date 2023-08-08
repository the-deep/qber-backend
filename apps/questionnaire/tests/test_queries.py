from main.tests import TestCase

from apps.user.factories import UserFactory
from apps.project.factories import ProjectFactory
from apps.questionnaire.models import Question
from apps.questionnaire.factories import QuestionnaireFactory, QuestionFactory


class TestQuestionnaireQuery(TestCase):
    class Query:
        QuestionnaireList = '''
            query MyQuery($projectID: ID!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  questionnaires(order: {id: ASC}) {
                    count
                    items {
                      id
                      title
                      projectId
                      createdAt
                      createdBy {
                        id
                      }
                      modifiedAt
                      modifiedBy {
                        id
                      }
                    }
                  }
                }
              }
            }
        '''

        Questionnaire = '''
            query MyQuery($projectID: ID!, $questionnaireID: ID!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  questionnaire(pk: $questionnaireID) {
                    id
                    title
                    projectId
                    createdAt
                    createdBy {
                      id
                    }
                    modifiedAt
                    modifiedBy {
                      id
                    }
                  }
                }
              }
            }
        '''

    def test_questionnaires(self):
        # Create some users
        user, user2 = UserFactory.create_batch(2)
        user_resource_params = {'created_by': user, 'modified_by': user}
        project1, project2 = ProjectFactory.create_batch(2, **user_resource_params)
        project1.add_member(user)
        project2.add_member(user2)

        p1_questionnaires = QuestionnaireFactory.create_batch(3, **user_resource_params, project=project1)
        p2_questionnaires = QuestionnaireFactory.create_batch(2, **user_resource_params, project=project2)

        # Without authentication -----
        content = self.query_check(
            self.Query.QuestionnaireList,
            assert_errors=True,
            variables={'projectID': str(project1.id)},
        )
        assert content['data'] is None

        # With authentication -----
        for user, project, questionnaires in [
            (user, project1, p1_questionnaires),
            (user, project2, None),
            (user2, project1, None),
            (user2, project2, p2_questionnaires),
        ]:
            self.force_login(user)
            content = self.query_check(
                self.Query.QuestionnaireList,
                variables={'projectID': str(project.id)},
            )
            if questionnaires is None:
                assert content['data']['private']['projectScope'] is None
                continue
            assert content['data']['private']['projectScope'] is not None, (
                content, user, project, questionnaires
            )
            assert content['data']['private']['projectScope']['questionnaires'] == {
                'count': len(questionnaires),
                'items': [
                    {
                        'id': str(questionnaire.pk),
                        'title': questionnaire.title,
                        'projectId': str(questionnaire.project_id),
                        'createdAt': self.gql_datetime(questionnaire.created_at),
                        'createdBy': {
                            'id': str(questionnaire.created_by_id),
                        },
                        'modifiedAt': self.gql_datetime(questionnaire.modified_at),
                        'modifiedBy': {
                            'id': str(questionnaire.modified_by_id),
                        },
                    }
                    for questionnaire in questionnaires
                ]
            }

    def test_questionnaire(self):
        # Create some users
        user = UserFactory.create()
        user_resource_params = {'created_by': user, 'modified_by': user}
        project = ProjectFactory.create(**user_resource_params)
        project.add_member(user)

        questionnaires = QuestionnaireFactory.create_batch(3, project=project, **user_resource_params)

        # Without authentication -----
        content = self.query_check(
            self.Query.Questionnaire,
            assert_errors=True,
            variables={'projectID': str(project.id)},
        )
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        for questionnaire in questionnaires:
            content = self.query_check(
                self.Query.Questionnaire,
                variables={
                    'projectID': str(project.id),
                    'questionnaireID': str(questionnaire.id),
                },
            )
            assert_msg = (content, user, questionnaire)
            assert content['data']['private']['projectScope'] is not None, assert_msg
            assert content['data']['private']['projectScope']['questionnaire'] == {
                'id': str(questionnaire.pk),
                'title': questionnaire.title,
                'projectId': str(questionnaire.project_id),
                'createdAt': self.gql_datetime(questionnaire.created_at),
                'createdBy': {
                    'id': str(questionnaire.created_by_id),
                },
                'modifiedAt': self.gql_datetime(questionnaire.modified_at),
                'modifiedBy': {
                    'id': str(questionnaire.modified_by_id),
                },
            }, assert_msg


class TestQuestionQuery(TestCase):
    class Query:
        QuestionList = '''
            query MyQuery($projectID: ID!, $filterData: QuestionFilter) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  questions(order: {id: ASC}, filters: $filterData) {
                    count
                    items {
                      id
                      questionnaireId
                      createdAt
                      createdBy {
                        id
                      }
                      modifiedAt
                      modifiedBy {
                        id
                      }
                      type
                      name
                      label
                      hint
                    }
                  }
                }
              }
            }
        '''

        Question = '''
            query MyQuery($projectID: ID!, $questionID: ID!) {
              private {
                id
                projectScope(pk: $projectID) {
                  id
                  question(pk: $questionID) {
                    id
                    questionnaireId
                    createdAt
                    createdBy {
                      id
                    }
                    modifiedAt
                    modifiedBy {
                      id
                    }
                    type
                    name
                    label
                    hint
                  }
                }
              }
            }
        '''

    def test_questions(self):
        # Create some users
        user = UserFactory.create()
        user_resource_params = {'created_by': user, 'modified_by': user}
        project = ProjectFactory.create(**user_resource_params)
        project.add_member(user)

        q1, q2, q3 = QuestionnaireFactory.create_batch(3, project=project, **user_resource_params)

        question_params = {**user_resource_params, 'type': Question.Type.DATE}
        q1_questions = QuestionFactory.create_batch(2, **question_params, questionnaire=q1, label='Who are you?')
        q2_questions = QuestionFactory.create_batch(3, **question_params, questionnaire=q2)
        q3_questions = QuestionFactory.create_batch(5, **question_params, questionnaire=q3)
        q3_questions[0].name = 'question-unique-0001'
        q3_questions[0].save(update_fields=('name',))

        # Without authentication -----
        content = self.query_check(
            self.Query.QuestionList,
            assert_errors=True,
            variables={'projectID': str(project.id)},
        )
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        for filter_data, questions in [
            ({'questionnaire': {'pk': str(q1.id)}}, q1_questions),
            ({'questionnaire': {'pk': str(q2.id)}}, q2_questions),
            ({'questionnaire': {'pk': str(q3.id)}}, q3_questions),
            ({'search': 'Who are you?'}, q1_questions),
            ({'name': {'exact': 'question-unique-0001'}}, [q3_questions[0]]),
        ]:
            content = self.query_check(
                self.Query.QuestionList,
                variables={
                    'projectID': str(project.id),
                    'filterData': filter_data,
                },
            )
            assert_msg = (content, user, filter_data, questions)
            assert content['data']['private']['projectScope'] is not None, assert_msg
            assert content['data']['private']['projectScope']['questions'] == {
                'count': len(questions),
                'items': [
                    {
                        'id': str(question.pk),
                        'questionnaireId': str(question.questionnaire_id),
                        'createdAt': self.gql_datetime(question.created_at),
                        'createdBy': {
                            'id': str(question.created_by_id),
                        },
                        'modifiedAt': self.gql_datetime(question.modified_at),
                        'modifiedBy': {
                            'id': str(question.modified_by_id),
                        },
                        'name': question.name,
                        'type': self.genum(question.type),
                        'label': question.label,
                        'hint': question.hint,
                    }
                    for question in questions
                ]
            }, assert_msg

    def test_question(self):
        # Create some users
        user = UserFactory.create()
        user_resource_params = {'created_by': user, 'modified_by': user}
        project = ProjectFactory.create(**user_resource_params)
        project.add_member(user)

        question_params = {**user_resource_params, 'type': Question.Type.DATE}
        q1 = QuestionnaireFactory.create(project=project, **user_resource_params)
        question, *_ = QuestionFactory.create_batch(4, **question_params, questionnaire=q1)

        # Without authentication -----
        content = self.query_check(
            self.Query.QuestionList,
            assert_errors=True,
            variables={
                'projectID': str(project.id),
                'questionID': str(question.id),
            },
        )
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        content = self.query_check(
            self.Query.Question,
            variables={
                'projectID': str(project.id),
                'questionID': str(question.id),
            },
        )
        assert content['data']['private']['projectScope'] is not None, content
        assert content['data']['private']['projectScope']['question'] == {
            'id': str(question.pk),
            'questionnaireId': str(question.questionnaire_id),
            'createdAt': self.gql_datetime(question.created_at),
            'createdBy': {
                'id': str(question.created_by_id),
            },
            'modifiedAt': self.gql_datetime(question.modified_at),
            'modifiedBy': {
                'id': str(question.modified_by_id),
            },
            'name': question.name,
            'type': self.genum(question.type),
            'label': question.label,
            'hint': question.hint,
        }, content
