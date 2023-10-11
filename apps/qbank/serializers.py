from django.db import transaction
from rest_framework import serializers

from apps.common.serializers import UserResourceSerializer
from apps.qbank.models import QuestionBank
from apps.qbank.tasks import import_task


class CreateQuestionBankSerializer(UserResourceSerializer):
    class Meta:
        model = QuestionBank
        fields = (
            'title',
            'description',
            'import_file',
        )

    def validate_import_file(self, import_file):
        # Basic extension check
        if not import_file.name.endswith('.xlsx'):
            raise serializers.ValidationError('Only XLSX file allowed. ')
        return import_file

    def update(self, _):
        raise Exception('Update not allowed')

    def create(self, data):
        instance = super().create(data)
        # Trigger import
        transaction.on_commit(
            lambda: import_task.delay(instance.pk)
        )
        return instance
