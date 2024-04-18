import gzip
import os
from pathlib import Path
from unittest import mock

from django.core.files.temp import NamedTemporaryFile

from main.tests import TestCase

from apps.common.models import GlobalPermission
from apps.user.factories import UserFactory
from apps.qbank.factories import QuestionBankFactory
from apps.qbank.models import QuestionBank
from apps.qbank.tasks import import_task

BASE_DIR = Path(__file__).resolve().parent


class TestQbankMutation(TestCase):
    class Query:
        Qbank = '''
            query Query($id: ID!) {
              private {
                questionBank(pk: $id) {
                  id
                  isActive
                  title
                  errors
                }
              }
            }
        '''

        ActiveQbank = '''
            query MyQuery {
              private {
                activeQuestionBank {
                  id
                  isActive
                }
              }
            }
        '''

    class Mutation:
        QbankCreate = '''
            mutation MyMutation($data: CreateQuestionBankInput!) {
              private {
                createQuestionBank(data: $data) {
                  errors
                  ok
                  result {
                    id
                    isActive
                    title
                    errors
                  }
                }
              }
            }
        '''

        QbankActivate = '''
            mutation MyMutation($id: ID!) {
              private {
                id
                activateQuestionBank(id: $id) {
                  ok
                  errors
                  result {
                    id
                    isActive
                    errors
                  }
                }
              }
            }
        '''

    @mock.patch('apps.qbank.serializers.import_task.delay')
    def test_create_qbank(self, import_task_mock):
        user = UserFactory.create()

        data = {
            'title': 'Question bank 1',
            'description': 'Basic description',
        }

        def _query_check(_id, **kwargs):
            return self.query_check(
                self.Query.Qbank,
                variables={
                    'id': _id,
                },
                **kwargs,
            )

        with (
            NamedTemporaryFile(suffix='.png') as invalid_file,
            gzip.GzipFile(os.path.join(BASE_DIR, 'xlsform-valid.xlsx.gz'), mode='rb') as clean_file,
            gzip.GzipFile(
                os.path.join(BASE_DIR, 'xlsform-invalid-name.xlsx.gz'),
                mode='rb'
            ) as xlsform_error_file,  # XLSForm Error
            gzip.GzipFile(
                os.path.join(BASE_DIR, 'xlsform-invalid.xlsx.gz'),
                mode='rb',
            ) as qber_error_file,  # Qber Error
        ):
            clean_file.name = clean_file.name.replace('.gz', '')
            xlsform_error_file.name = xlsform_error_file.name.replace('.gz', '')
            qber_error_file.name = qber_error_file.name.replace('.gz', '')

            invalid_file.write(b'test-data')

            def _mutation_check(data, file=None, **kwargs):
                if file is None:
                    file = clean_file
                file.seek(0)
                return self.query_check(
                    self.Mutation.QbankCreate,
                    variables={
                        'data': data,
                    },
                    files={
                        't_file': file,
                    },
                    map={
                        't_file': ['variables.data.importFile']
                    },
                    **kwargs,
                )

            # Without login
            _mutation_check(data=data, assert_errors=True)
            # With login - Without permission
            self.force_login(user)
            response = _mutation_check(data=data)['data']['private']['createQuestionBank']
            assert response['ok'] is False
            assert response['errors'] not in ([], None)
            # - Without permission
            self.global_permissions[GlobalPermission.Type.UPLOAD_QBANK].add_user(user)
            with self.captureOnCommitCallbacks(execute=True):
                response_success = _mutation_check(data=data)['data']['private']['createQuestionBank']
            with self.captureOnCommitCallbacks(execute=True):
                response_xlsform_error = _mutation_check(
                    data=data, file=xlsform_error_file)['data']['private']['createQuestionBank']
            with self.captureOnCommitCallbacks(execute=True):
                response_qber_error = _mutation_check(
                    data=data, file=qber_error_file)['data']['private']['createQuestionBank']
            with self.captureOnCommitCallbacks(execute=True):
                response_invalid = _mutation_check(data=data, file=invalid_file)['data']['private']['createQuestionBank']
            qbank_success_id = int(response_success['result'].pop('id'))
            qbank_xlsform_error_id = int(response_xlsform_error['result'].pop('id'))
            qbank_qber_error_id = int(response_qber_error['result'].pop('id'))

            import_task_mock.assert_has_calls([
                mock.call(qbank_success_id),
                mock.call(qbank_xlsform_error_id),
                mock.call(qbank_qber_error_id),
            ])
            assert response_success['ok'] is True
            assert response_xlsform_error['ok'] is True
            assert response_qber_error['ok'] is True
            assert response_invalid['ok'] is False

            assert response_success['result'] == \
                response_qber_error['result'] == \
                response_xlsform_error['result'] == {
                'title': data['title'],
                'isActive': False,
                'errors': [],
            }
            # Run import task
            import_task(qbank_success_id)
            import_task(qbank_xlsform_error_id)
            import_task(qbank_qber_error_id)
            qbank_success = QuestionBank.objects.get(pk=qbank_success_id)
            qbank_xlsform_error = QuestionBank.objects.get(pk=qbank_xlsform_error_id)
            qbank_qber_error = QuestionBank.objects.get(pk=qbank_qber_error_id)
            # Success
            response = _query_check(qbank_success_id)['data']['private']['questionBank']
            assert qbank_success.status == QuestionBank.Status.SUCCESS
            assert qbank_success.errors == []
            assert response == {
                'id': str(qbank_success_id),
                'title': data['title'],
                'isActive': False,
                'errors': []
            }
            del response
            # Failures - XLSForm Structure
            response = _query_check(qbank_xlsform_error_id)['data']['private']['questionBank']
            assert qbank_xlsform_error.status == QuestionBank.Status.FAILURE
            assert qbank_xlsform_error.errors != []
            assert response.pop('errors') == ['On the choices sheet there is a option with no name. [list_name : list_name]']
            assert response == {
                'id': str(qbank_xlsform_error_id),
                'title': data['title'],
                'isActive': False,
            }
            del response
            # Failures - Qber Structure
            response = _query_check(qbank_qber_error_id)['data']['private']['questionBank']
            assert qbank_qber_error.status == QuestionBank.Status.FAILURE
            assert qbank_qber_error.errors != []
            assert response.pop('errors') != []
            assert response == {
                'id': str(qbank_qber_error_id),
                'title': data['title'],
                'isActive': False,
            }
            del response

    def test_activate_qbank(self):
        user = UserFactory.create()
        ur_params = dict(created_by=user, modified_by=user)
        qbank = QuestionBankFactory.create(**ur_params)

        def _check_qb_active_status(is_active):
            qbank.refresh_from_db()
            assert qbank.is_active == is_active

        def _mutation_check(**kwargs):
            return self.query_check(
                self.Mutation.QbankActivate,
                variables={
                    'id': str(qbank.pk),
                },
                **kwargs,
            )

        def _query_check(**kwargs):
            return self.query_check(
                self.Query.ActiveQbank,
                **kwargs,
            )

        # Without login
        _mutation_check(assert_errors=True)
        _query_check(assert_errors=True)
        # With login - Without permission
        self.force_login(user)
        # -- ActiveQbank Query
        assert _query_check()['data']['private']['activeQuestionBank'] is None
        # -- Mutation Query
        response = _mutation_check()['data']['private']['activateQuestionBank']
        assert response['ok'] is False
        assert response['errors'] not in ([], None)
        # - Without correct permission
        self.global_permissions[GlobalPermission.Type.UPLOAD_QBANK].add_user(user)
        response = _mutation_check()['data']['private']['activateQuestionBank']
        assert response['ok'] is False
        assert response['errors'] not in ([], None)
        # - Without permission
        self.global_permissions[GlobalPermission.Type.ACTIVATE_QBANK].add_user(user)
        # -- Still None
        assert _query_check()['data']['private']['activeQuestionBank'] is None
        for qbank_status, is_active_status in [
            # Order matters
            (QuestionBank.Status.PENDING, False),
            (QuestionBank.Status.STARTED, False),
            (QuestionBank.Status.FAILURE, False),
            (QuestionBank.Status.SUCCESS, True),
        ]:
            qbank.status = qbank_status
            qbank.save(update_fields=('status',))
            response = _mutation_check()['data']['private']['activateQuestionBank']
            assert response['ok'] is is_active_status
            _check_qb_active_status(is_active_status)

        # Check query as well
        response = _query_check()['data']['private']['activeQuestionBank']
        assert response == {
            'id': str(qbank.id),
            'isActive': True,
        }
