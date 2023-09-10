from rest_framework import serializers
from django.db import transaction

from .models import QuestionnaireExport
from .tasks import export_task


class QuestionnaireExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireExport
        fields = (
            'type',
            'questionnaire',
        )

    instance: QuestionnaireExport

    def create(self, data):
        data['exported_by'] = self.context['request'].user
        export = super().create(data)
        transaction.on_commit(
            lambda: export.set_task_id(
                export_task.delay(export.id).id
            )
        )
        return export

    def update(self, _):
        raise serializers.ValidationError('Update not allowed')
