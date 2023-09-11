from main.tests import TestCase

from django.test import override_settings

from apps.user.factories import UserFactory
from apps.project.factories import ProjectFactory
from apps.export.factories import QuestionnaireExportFactory
from apps.questionnaire.factories import QuestionnaireFactory


class TestExportQuery(TestCase):
    class Query:
        EXPORT = '''
            query MyQuery($projectId: ID!, $questionnaireExportId: ID!) {
              private {
                projectScope(pk: $projectId) {
                  id
                  questionnaireExport(pk: $questionnaireExportId) {
                    id
                    type
                    typeDisplay
                    status
                    statusDisplay
                    exportedAt
                    startedAt
                    endedAt
                    exportedBy {
                      id
                    }
                    file {
                      url
                      name
                    }
                  }
                }
              }
            }
        '''

        EXPORTS = '''
            query MyQuery($projectId: ID!) {
              private {
                projectScope(pk: $projectId) {
                  id
                  questionnaireExports(order: {id: ASC}) {
                    count
                    items {
                      id
                      type
                      typeDisplay
                      status
                      statusDisplay
                      exportedAt
                      startedAt
                      endedAt
                      exportedBy {
                        id
                      }
                      file {
                        url
                        name
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
        cls.user1, cls.user2, cls.other_user = UserFactory.create_batch(3)

        user_resource_params = {'created_by': cls.user1, 'modified_by': cls.user1}
        cls.project = ProjectFactory.create(**user_resource_params)
        cls.project.add_member(cls.user1)
        cls.project.add_member(cls.user2)

        q1, _ = QuestionnaireFactory.create_batch(2, project=cls.project, **user_resource_params)

        cls.exports = QuestionnaireExportFactory.create_batch(3, exported_by=cls.user1, questionnaire=q1)

    def test_export(self):
        project = self.project
        export = self.exports[0]
        variables = {
            'projectId': self.gID(project.id),
            'questionnaireExportId': self.gID(export.id),
        }

        # Without authentication -----
        self.query_check(self.Query.EXPORTS, variables=variables, assert_errors=True)

        # With authentication (Without access to project) -----
        self.force_login(self.other_user)
        content = self.query_check(self.Query.EXPORT, variables=variables)
        # assert content['data']['private']['projectScope']['questionnaireExport'] is None
        assert content['data']['private']['projectScope'] is None

        # With authentication (Without access to export) -----
        self.force_login(self.user2)
        content = self.query_check(self.Query.EXPORT, variables=variables)
        # assert content['data']['private']['projectScope']['questionnaireExport'] is None
        assert content['data']['private']['projectScope']['questionnaireExport'] is None

        # With Access
        self.force_login(self.user1)
        content = self.query_check(self.Query.EXPORT, variables=variables)
        assert content['data']['private']['projectScope']['questionnaireExport'] == {
            'id': self.gID(export.id),
            'type': self.genum(export.type),
            'typeDisplay': export.get_type_display(),
            'status': self.genum(export.status),
            'statusDisplay': export.get_status_display(),
            'exportedAt': self.gdatetime(export.exported_at),
            'startedAt': self.gdatetime(export.started_at),
            'endedAt': self.gdatetime(export.ended_at),
            'exportedBy': {
                'id': self.gID(export.exported_by_id),
            },
            'file': {
                'url': self.get_media_url(export.file.name),
                'name': export.file.name,
            },
        }

    def test_exports(self):
        project = self.project
        exports = self.exports
        variables = {
            'projectId': self.gID(project.id),
        }

        # Without authentication -----
        self.query_check(self.Query.EXPORTS, variables=variables, assert_errors=True)

        # With authentication (Without access) -----
        self.force_login(self.other_user)
        content = self.query_check(self.Query.EXPORTS, variables=variables)
        # assert content['data']['private']['projectScope']['questionnaireExport'] is None
        assert content['data']['private']['projectScope'] is None

        # With Access
        for backend_storage in (
            'django.core.files.storage.FileSystemStorage',
            'main.storages.S3MediaStorage',
        ):
            with override_settings(
                STORAGES={
                    'default': {
                        'BACKEND': backend_storage,
                    },
                },
            ):
                for user_, exports_ in [
                        (self.user1, exports),
                        (self.user2, []),
                ]:
                    self.force_login(user_)
                    content = self.query_check(self.Query.EXPORTS, variables=variables)
                    assert content['data']['private']['projectScope']['questionnaireExports'] == {
                        'count': len(exports_),
                        'items': [
                            {
                                'id': self.gID(export.id),
                                'type': self.genum(export.type),
                                'typeDisplay': export.get_type_display(),
                                'status': self.genum(export.status),
                                'statusDisplay': export.get_status_display(),
                                'exportedAt': self.gdatetime(export.exported_at),
                                'startedAt': self.gdatetime(export.started_at),
                                'endedAt': self.gdatetime(export.ended_at),
                                'exportedBy': {
                                    'id': self.gID(export.exported_by_id),
                                },
                                'file': {
                                    'name': export.file.name,
                                    'url': (
                                        f'/media/{export.file.name}'
                                        if backend_storage == 'main.storages.S3MediaStorage'
                                        else
                                        self.get_media_url(export.file.name)
                                    ),
                                }
                            }
                            for export in exports_
                        ]
                    }
