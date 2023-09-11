from unittest.mock import patch

from main.tests import TestCase

from apps.user.factories import UserFactory
from apps.project.factories import ProjectFactory
from apps.project.models import ProjectMembership
from apps.export.models import QuestionnaireExport
from apps.questionnaire.factories import QuestionnaireFactory


class TestExportMutation(TestCase):
    class Mutation:
        CREATE_EXPORT = '''
            mutation MyMutation(
                $projectId: ID!,
                $data: QuestionnaireExportCreateInput!
            ) {
              private {
                id
                projectScope(pk: $projectId) {
                  id
                  createQuestionnaireExport(data: $data) {
                    ok
                    errors
                    result {
                      id
                      type
                      typeDisplay
                      statusDisplay
                      status
                      startedAt
                      exportedAt
                      endedAt
                      questionnaireId
                      exportedBy {
                        id
                      }
                      file {
                        name
                        url
                      }
                    }
                  }
                }
              }
            }
        '''

        DELETE_EXPORT = '''
            mutation MyMutation(
                $projectId: ID!,
                $questionnaireId: ID!
            ) {
              private {
                id
                projectScope(pk: $projectId) {
                  id
                  deleteQuestionnaireExport(id: $questionnaireId) {
                    ok
                    errors
                    result {
                      id
                      type
                      typeDisplay
                      statusDisplay
                      status
                      startedAt
                      exportedAt
                      endedAt
                      questionnaireId
                      exportedBy {
                        id
                        displayName
                      }
                      file {
                        name
                        url
                      }
                    }
                  }
                }
              }
            }
        '''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user, cls.ro_user, cls.other_user = UserFactory.create_batch(3)

        user_resource_params = {'created_by': cls.user, 'modified_by': cls.user}
        cls.project = ProjectFactory.create(**user_resource_params)
        cls.project.add_member(cls.user)
        cls.project.add_member(cls.ro_user, role=ProjectMembership.Role.VIEWER)

        cls.q1, _ = QuestionnaireFactory.create_batch(2, project=cls.project, **user_resource_params)

    @patch('apps.export.serializers.export_task.delay')
    def test_export(self, export_task_mock):
        class DummyCeleryTaskResponse():
            id = 'random-async-task-id'

        variables = {
            'projectId': self.gID(self.project.id),
            'data': {
                'type': self.genum(QuestionnaireExport.Type.XLSFORM),
                'questionnaire': self.gID(self.q1.pk),
            },
        }

        export_task_mock.return_value = DummyCeleryTaskResponse()
        # Without authentication -----
        with self.captureOnCommitCallbacks(execute=True):
            self.query_check(self.Mutation.CREATE_EXPORT, variables=variables, assert_errors=True)
        export_task_mock.assert_not_called()

        # With authentication (Without access to project) -----
        self.force_login(self.other_user)
        with self.captureOnCommitCallbacks(execute=True):
            content = self.query_check(self.Mutation.CREATE_EXPORT, variables=variables)
        export_task_mock.assert_not_called()
        # assert content['data']['private']['projectScope']['questionnaireExport'] is None
        assert content['data']['private']['projectScope'] is None

        # With authentication (Without access to export) -----
        self.force_login(self.ro_user)
        with self.captureOnCommitCallbacks(execute=True):
            content = self.query_check(self.Mutation.CREATE_EXPORT, variables=variables)
        export_task_mock.assert_not_called()
        # assert content['data']['private']['projectScope']['questionnaireExport'] is None
        assert content['data']['private']['projectScope']['createQuestionnaireExport']['ok'] is False
        assert content['data']['private']['projectScope']['createQuestionnaireExport']['errors'] is not None

        # With Access
        self.force_login(self.user)
        with self.captureOnCommitCallbacks(execute=True):
            content = self.query_check(
                self.Mutation.CREATE_EXPORT,
                variables=variables
            )['data']['private']['projectScope']['createQuestionnaireExport']
        export_task_mock.assert_called_once()
        assert content['ok'] is True
        assert content['errors'] is None
        export = QuestionnaireExport.objects.get(pk=content['result']['id'])
        assert export.get_task_id() == DummyCeleryTaskResponse.id
        assert content['result'] == {
            'id': self.gID(export.pk),
            'type': self.genum(QuestionnaireExport.Type.XLSFORM),
            'typeDisplay': export.get_type_display(),
            'status': self.genum(QuestionnaireExport.Status.PENDING),
            'statusDisplay': export.get_status_display(),
            'exportedAt': self.gdatetime(export.exported_at),
            'startedAt': self.gdatetime(export.started_at),
            'endedAt': self.gdatetime(export.ended_at),
            'exportedBy': {
                'id': self.gID(export.exported_by_id),
            },
            'file': None,
            'questionnaireId': self.gID(self.q1.pk),
        }
