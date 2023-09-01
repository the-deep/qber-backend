from main.tests import TestCase

from apps.user.factories import UserFactory
from apps.project.factories import ProjectFactory
from apps.questionnaire.models import Question
from apps.questionnaire.factories import (
    QuestionnaireFactory,
    QuestionFactory,
    QuestionLeafGroupFactory,
    ChoiceCollectionFactory,
    ChoiceFactory,
)


class TestQuestionnaireQuery(TestCase):
    class Query:
        QuestionnaireList = '''
            query MyQuery($projectId: ID!) {
              private {
                id
                projectScope(pk: $projectId) {
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
            query MyQuery($projectId: ID!, $questionnaireId: ID!) {
              private {
                id
                projectScope(pk: $projectId) {
                  id
                  questionnaire(pk: $questionnaireId) {
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
            variables={'projectId': self.gID(project1.id)},
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
                variables={
                    'projectId': self.gID(project.id)
                },
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
                        'id': self.gID(questionnaire.pk),
                        'title': questionnaire.title,
                        'projectId': self.gID(questionnaire.project_id),
                        'createdAt': self.gdatetime(questionnaire.created_at),
                        'createdBy': {
                            'id': self.gID(questionnaire.created_by_id),
                        },
                        'modifiedAt': self.gdatetime(questionnaire.modified_at),
                        'modifiedBy': {
                            'id': self.gID(questionnaire.modified_by_id),
                        },
                    }
                    for questionnaire in questionnaires
                ]
            }

    def test_questionnaire(self):
        # Create some users
        user = UserFactory.create()
        user_resource_params = {'created_by': user, 'modified_by': user}
        project, project2 = ProjectFactory.create_batch(2, **user_resource_params)

        questionnaires = QuestionnaireFactory.create_batch(3, project=project, **user_resource_params)
        q2 = QuestionnaireFactory.create(project=project2, **user_resource_params)

        variables = {'projectId': self.gID(project.id)}
        # Without authentication -----
        content = self.query_check(
            self.Query.Questionnaire,
            assert_errors=True,
            variables=variables,
        )
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        # -- Without membership
        content = self.query_check(
            self.Query.Questionnaire,
            variables={
                **variables,
                'questionnaireId': self.gID(questionnaires[0].id),
            },
        )
        assert content['data']['private']['projectScope'] is None, content
        # -- With membership
        project.add_member(user)
        for questionnaire in questionnaires:
            content = self.query_check(
                self.Query.Questionnaire,
                variables={
                    **variables,
                    'questionnaireId': self.gID(questionnaire.id),
                },
            )
            assert_msg = (content, user, questionnaire)
            assert content['data']['private']['projectScope'] is not None, assert_msg
            assert content['data']['private']['projectScope']['questionnaire'] == {
                'id': self.gID(questionnaire.pk),
                'title': questionnaire.title,
                'projectId': self.gID(questionnaire.project_id),
                'createdAt': self.gdatetime(questionnaire.created_at),
                'createdBy': {
                    'id': self.gID(questionnaire.created_by_id),
                },
                'modifiedAt': self.gdatetime(questionnaire.modified_at),
                'modifiedBy': {
                    'id': self.gID(questionnaire.modified_by_id),
                },
            }, assert_msg

        # Another project questionnaire
        variables['questionnaireId'] = self.gID(q2.id)
        content = self.query_check(
            self.Query.Questionnaire,
            variables=variables,
        )
        assert content['data']['private']['projectScope']['questionnaire'] is None, content


class TestQuestionGroupQuery(TestCase):
    class Query:
        QuestionGroupList = '''
            query MyQuery($projectId: ID!, $filterData: QuestionLeafGroupFilter) {
              private {
                projectScope(pk: $projectId) {
                  leafGroups(order: {id: ASC}, filters: $filterData) {
                    count
                    items {
                      id
                      questionnaireId
                      name
                      type
                      category1
                      category2
                      category3
                      category4
                      relevant
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

        QuestionGroup = '''
            query MyQuery($projectId: ID!, $questionGroupId: ID!) {
              private {
                projectScope(pk: $projectId) {
                  leafGroup(pk: $questionGroupId) {
                    id
                    questionnaireId
                    name
                    relevant
                    type
                    category1
                    category2
                    category3
                    category4
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

    def test_leaf_groups(self):
        # Create some users
        user = UserFactory.create()
        user_resource_params = {'created_by': user, 'modified_by': user}
        project = ProjectFactory.create(**user_resource_params)
        project.add_member(user)

        q1, q2, q3 = QuestionnaireFactory.create_batch(3, project=project, **user_resource_params)

        q1_groups = QuestionLeafGroupFactory.static_generator(2, **user_resource_params, questionnaire=q1)
        q2_groups = QuestionLeafGroupFactory.static_generator(3, **user_resource_params, questionnaire=q2)
        q3_groups = QuestionLeafGroupFactory.static_generator(5, **user_resource_params, questionnaire=q3)
        q3_groups[0].name = 'question-group-unique-0001'
        q3_groups[0].save(update_fields=('name',))

        variables = {'projectId': self.gID(project.id)}
        # Without authentication -----
        content = self.query_check(
            self.Query.QuestionGroupList,
            assert_errors=True,
            variables=variables,
        )
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        for filter_data, question_leaf_groups in [
            ({'questionnaire': {'pk': self.gID(q1.id)}}, q1_groups),
            ({'questionnaire': {'pk': self.gID(q2.id)}}, q2_groups),
            ({'questionnaire': {'pk': self.gID(q3.id)}}, q3_groups),
            ({'name': {'exact': 'question-group-unique-0001'}}, [q3_groups[0]]),
        ]:
            content = self.query_check(
                self.Query.QuestionGroupList,
                variables={
                    **variables,
                    'filterData': filter_data,
                },
            )
            assert_msg = (content, user, filter_data, question_leaf_groups)
            assert content['data']['private']['projectScope'] is not None, assert_msg
            assert content['data']['private']['projectScope']['leafGroups'] == {
                'count': len(question_leaf_groups),
                'items': [
                    {
                        'id': self.gID(question_leaf_group.pk),
                        'questionnaireId': self.gID(question_leaf_group.questionnaire_id),
                        'createdAt': self.gdatetime(question_leaf_group.created_at),
                        'createdBy': {
                            'id': self.gID(question_leaf_group.created_by_id),
                        },
                        'modifiedAt': self.gdatetime(question_leaf_group.modified_at),
                        'modifiedBy': {
                            'id': self.gID(question_leaf_group.modified_by_id),
                        },
                        'name': question_leaf_group.name,
                        'relevant': question_leaf_group.relevant,
                        'type': self.genum(question_leaf_group.type),
                        'category1': self.genum(question_leaf_group.category_1),
                        'category2': self.genum(question_leaf_group.category_2),
                        'category3': self.genum(question_leaf_group.category_3),
                        'category4': self.genum(question_leaf_group.category_4),
                    }
                    for question_leaf_group in question_leaf_groups
                ]
            }, assert_msg

    def test_leaf_group(self):
        # Create some users
        user = UserFactory.create()
        user_resource_params = {'created_by': user, 'modified_by': user}
        project, project2 = ProjectFactory.create_batch(2, **user_resource_params)

        q1 = QuestionnaireFactory.create(project=project, **user_resource_params)
        q2 = QuestionnaireFactory.create(project=project2, **user_resource_params)
        q1_group, *_ = QuestionLeafGroupFactory.static_generator(4, **user_resource_params, questionnaire=q1)
        [q2_group] = QuestionLeafGroupFactory.static_generator(1, **user_resource_params, questionnaire=q2)

        variables = {
            'projectId': self.gID(project.id),
            'questionGroupId': self.gID(q1_group.id),
        }
        # Without authentication -----
        content = self.query_check(
            self.Query.QuestionGroup,
            assert_errors=True,
            variables=variables,
        )
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        # -- Without membership
        content = self.query_check(self.Query.QuestionGroup, variables=variables)
        assert content['data']['private']['projectScope'] is None, content
        # -- With membership
        project.add_member(user)
        content = self.query_check(self.Query.QuestionGroup, variables=variables)
        assert content['data']['private']['projectScope'] is not None, content
        assert content['data']['private']['projectScope']['leafGroup'] == {
            'id': self.gID(q1_group.pk),
            'questionnaireId': self.gID(q1_group.questionnaire_id),
            'createdAt': self.gdatetime(q1_group.created_at),
            'createdBy': {
                'id': self.gID(q1_group.created_by_id),
            },
            'modifiedAt': self.gdatetime(q1_group.modified_at),
            'modifiedBy': {
                'id': self.gID(q1_group.modified_by_id),
            },
            'name': q1_group.name,
            'relevant': q1_group.relevant,
            'type': self.genum(q1_group.type),
            'category1': self.genum(q1_group.category_1),
            'category2': self.genum(q1_group.category_2),
            'category3': self.genum(q1_group.category_3),
            'category4': self.genum(q1_group.category_4),
        }, content

        # Another project question group
        variables['questionGroupId'] = self.gID(q2_group.id)
        content = self.query_check(
            self.Query.QuestionGroup,
            variables=variables,
        )
        assert content['data']['private']['projectScope']['leafGroup'] is None, content


class TestChoiceCollectionQuery(TestCase):
    class Query:
        ChoiceCollectionList = '''
            query MyQuery($projectId: ID!, $filterData: QuestionChoiceCollectionFilter) {
              private {
                projectScope(pk: $projectId) {
                  choiceCollections(order: {id: ASC}, filters: $filterData) {
                    count
                    items {
                      id
                      label
                      name
                      questionnaireId
                      modifiedAt
                      modifiedBy {
                        id
                      }
                      createdAt
                      createdBy {
                        id
                      }
                      choices {
                        id
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

        ChoiceCollection = '''
            query MyQuery($projectId: ID!, $choiceCollectionID: ID!) {
              private {
                projectScope(pk: $projectId) {
                  choiceCollection(pk: $choiceCollectionID) {
                    id
                    label
                    name
                    questionnaireId
                    modifiedAt
                    modifiedBy {
                      id
                    }
                    createdAt
                    createdBy {
                      id
                    }
                    choices {
                      id
                      label
                      name
                      collectionId
                    }
                  }
                }
              }
            }
        '''

    def test_choice_collections(self):
        # Create some users
        user = UserFactory.create()
        user_resource_params = {'created_by': user, 'modified_by': user}
        project = ProjectFactory.create(**user_resource_params)
        project.add_member(user)

        q1, q2, q3 = QuestionnaireFactory.create_batch(3, project=project, **user_resource_params)

        q1_choice_collections = ChoiceCollectionFactory.create_batch(
            2,
            **user_resource_params,
            questionnaire=q1,
            label='[Choices] Gender',
        )
        q2_choice_collections = ChoiceCollectionFactory.create_batch(3, **user_resource_params, questionnaire=q2)
        q3_choice_collections = ChoiceCollectionFactory.create_batch(5, **user_resource_params, questionnaire=q3)
        q3_choice_collections[0].name = 'question-choice-collection-unique-0001'
        q3_choice_collections[0].save(update_fields=('name',))

        variables = {'projectId': self.gID(project.id)}
        # Without authentication -----
        content = self.query_check(
            self.Query.ChoiceCollectionList,
            assert_errors=True,
            variables=variables,
        )
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        for filter_data, question_choice_collections in [
            ({'questionnaire': {'pk': self.gID(q1.id)}}, q1_choice_collections),
            ({'questionnaire': {'pk': self.gID(q2.id)}}, q2_choice_collections),
            ({'questionnaire': {'pk': self.gID(q3.id)}}, q3_choice_collections),
            ({'label': {'exact': '[Choices] Gender'}}, q1_choice_collections),
            ({'name': {'exact': 'question-choice-collection-unique-0001'}}, [q3_choice_collections[0]]),
        ]:
            content = self.query_check(
                self.Query.ChoiceCollectionList,
                variables={
                    **variables,
                    'filterData': filter_data,
                },
            )
            assert_msg = (content, user, filter_data, question_choice_collections)
            assert content['data']['private']['projectScope'] is not None, assert_msg
            assert content['data']['private']['projectScope']['choiceCollections'] == {
                'count': len(question_choice_collections),
                'items': [
                    {
                        'id': self.gID(question_choice_collection.pk),
                        'questionnaireId': self.gID(question_choice_collection.questionnaire_id),
                        'name': question_choice_collection.name,
                        'label': question_choice_collection.label,
                        'createdAt': self.gdatetime(question_choice_collection.created_at),
                        'createdBy': {
                            'id': self.gID(question_choice_collection.created_by_id),
                        },
                        'modifiedAt': self.gdatetime(question_choice_collection.modified_at),
                        'modifiedBy': {
                            'id': self.gID(question_choice_collection.modified_by_id),
                        },
                        'choices': [],
                    }
                    for question_choice_collection in question_choice_collections
                ]
            }, assert_msg

    def test_choice_collection(self):
        # Create some users
        user = UserFactory.create()
        user_resource_params = {'created_by': user, 'modified_by': user}
        project, project2 = ProjectFactory.create_batch(2, **user_resource_params)

        q1 = QuestionnaireFactory.create(project=project, **user_resource_params)
        q2 = QuestionnaireFactory.create(project=project2, **user_resource_params)
        q1_question_choice_collection, *_ = ChoiceCollectionFactory.create_batch(4, **user_resource_params, questionnaire=q1)
        q2_question_choice_collection = ChoiceCollectionFactory.create(**user_resource_params, questionnaire=q2)

        q1_question_choice_collection_choices = ChoiceFactory.create_batch(
            4,
            collection=q1_question_choice_collection
        )

        variables = {
            'projectId': self.gID(project.id),
            'choiceCollectionID': self.gID(q1_question_choice_collection.id),
        }
        # Without authentication -----
        content = self.query_check(
            self.Query.ChoiceCollection,
            assert_errors=True,
            variables=variables,
        )
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        # -- Without membership
        content = self.query_check(self.Query.ChoiceCollection, variables=variables)
        assert content['data']['private']['projectScope'] is None, content
        # -- With membership
        project.add_member(user)
        content = self.query_check(self.Query.ChoiceCollection, variables=variables)
        assert content['data']['private']['projectScope'] is not None, content
        assert content['data']['private']['projectScope']['choiceCollection'] == {
            'id': self.gID(q1_question_choice_collection.pk),
            'questionnaireId': self.gID(q1_question_choice_collection.questionnaire_id),
            'name': q1_question_choice_collection.name,
            'label': q1_question_choice_collection.label,
            'createdAt': self.gdatetime(q1_question_choice_collection.created_at),
            'createdBy': {
                'id': self.gID(q1_question_choice_collection.created_by_id),
            },
            'modifiedAt': self.gdatetime(q1_question_choice_collection.modified_at),
            'modifiedBy': {
                'id': self.gID(q1_question_choice_collection.modified_by_id),
            },
            'choices': [
                {
                    'id': self.gID(choice.pk),
                    'label': choice.label,
                    'name': choice.name,
                    'collectionId': self.gID(q1_question_choice_collection.id),
                }
                for choice in q1_question_choice_collection_choices
            ],
        }, content

        # Another project question choice collection
        variables['choiceCollectionID'] = self.gID(q2_question_choice_collection.id)
        content = self.query_check(
            self.Query.ChoiceCollection,
            variables=variables,
        )
        assert content['data']['private']['projectScope']['choiceCollection'] is None, content


class TestQuestionQuery(TestCase):
    class Query:
        QuestionList = '''
            query MyQuery($projectId: ID!, $filterData: QuestionFilter) {
              private {
                id
                projectScope(pk: $projectId) {
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
            query MyQuery($projectId: ID!, $questionID: ID!) {
              private {
                id
                projectScope(pk: $projectId) {
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
                    choiceCollection {
                      id
                      name
                      label
                      choices {
                        id
                        name
                        label
                      }
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

        [group1] = QuestionLeafGroupFactory.static_generator(1, **user_resource_params, questionnaire=q1)
        [group2] = QuestionLeafGroupFactory.static_generator(1, **user_resource_params, questionnaire=q2)
        [group3] = QuestionLeafGroupFactory.static_generator(1, **user_resource_params, questionnaire=q3)

        question_params = {**user_resource_params, 'type': Question.Type.DATE}
        q1_questions = QuestionFactory.create_batch(
            2, **question_params, questionnaire=q1, leaf_group=group1, label='Who are you?')
        q2_questions = QuestionFactory.create_batch(3, **question_params, questionnaire=q2, leaf_group=group2)
        q3_questions = QuestionFactory.create_batch(5, **question_params, questionnaire=q3, leaf_group=group3)
        q3_questions[0].name = 'question-unique-0001'
        q3_questions[0].save(update_fields=('name',))

        variables = {'projectId': self.gID(project.id)}
        # Without authentication -----
        content = self.query_check(
            self.Query.QuestionList,
            assert_errors=True,
            variables=variables,
        )
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        for filter_data, questions in [
            ({'questionnaire': {'pk': self.gID(q1.id)}}, q1_questions),
            ({'questionnaire': {'pk': self.gID(q2.id)}}, q2_questions),
            ({'questionnaire': {'pk': self.gID(q3.id)}}, q3_questions),
            ({'label': {'exact': 'Who are you?'}}, q1_questions),
            ({'name': {'exact': 'question-unique-0001'}}, [q3_questions[0]]),
        ]:
            content = self.query_check(
                self.Query.QuestionList,
                variables={
                    **variables,
                    'filterData': filter_data,
                },
            )
            assert_msg = (content, user, filter_data, questions)
            assert content['data']['private']['projectScope'] is not None, assert_msg
            assert content['data']['private']['projectScope']['questions'] == {
                'count': len(questions),
                'items': [
                    {
                        'id': self.gID(question.pk),
                        'questionnaireId': self.gID(question.questionnaire_id),
                        'createdAt': self.gdatetime(question.created_at),
                        'createdBy': {
                            'id': self.gID(question.created_by_id),
                        },
                        'modifiedAt': self.gdatetime(question.modified_at),
                        'modifiedBy': {
                            'id': self.gID(question.modified_by_id),
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
        project, project2 = ProjectFactory.create_batch(2, **user_resource_params)

        question_params = {**user_resource_params, 'type': Question.Type.DATE}
        q1 = QuestionnaireFactory.create(project=project, **user_resource_params)
        q2 = QuestionnaireFactory.create(project=project2, **user_resource_params)

        [group1] = QuestionLeafGroupFactory.static_generator(1, **user_resource_params, questionnaire=q1)
        [group2] = QuestionLeafGroupFactory.static_generator(1, **user_resource_params, questionnaire=q2)

        q1_choice_collection = ChoiceCollectionFactory.create(**user_resource_params, questionnaire=q1)

        question, *_ = QuestionFactory.create_batch(
            4,
            **question_params,
            questionnaire=q1,
            leaf_group=group1,
            choice_collection=q1_choice_collection,
        )
        question2 = QuestionFactory.create(**question_params, questionnaire=q2, leaf_group=group2)

        choice_collection_response = {
            'id': self.gID(q1_choice_collection.pk),
            'name': self.gID(q1_choice_collection.name),
            'label': self.gID(q1_choice_collection.label),
            'choices': [
                {
                    'id': self.gID(choice.pk),
                    'name': self.gID(choice.name),
                    'label': self.gID(choice.label),
                }
                for choice in q1_choice_collection.choice_set.all()
            ],
        }

        variables = {
            'projectId': self.gID(project.id),
            'questionID': self.gID(question.id),
        }
        # Without authentication -----
        content = self.query_check(
            self.Query.Question,
            assert_errors=True,
            variables=variables,
        )
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        # Without membership
        content = self.query_check(self.Query.Question, variables=variables)
        assert content['data']['private']['projectScope'] is None, content
        # With membership
        project.add_member(user)
        content = self.query_check(self.Query.Question, variables=variables)
        assert content['data']['private']['projectScope'] is not None, content
        assert content['data']['private']['projectScope']['question'] == {
            'id': self.gID(question.pk),
            'questionnaireId': self.gID(question.questionnaire_id),
            'createdAt': self.gdatetime(question.created_at),
            'createdBy': {
                'id': self.gID(question.created_by_id),
            },
            'modifiedAt': self.gdatetime(question.modified_at),
            'modifiedBy': {
                'id': self.gID(question.modified_by_id),
            },
            'name': question.name,
            'type': self.genum(question.type),
            'label': question.label,
            'hint': question.hint,
            'choiceCollection': choice_collection_response,
        }, content

        # Another project question
        variables['questionID'] = self.gID(question2.id)
        content = self.query_check(
            self.Query.Question,
            variables=variables,
        )
        assert content['data']['private']['projectScope']['question'] is None, content
