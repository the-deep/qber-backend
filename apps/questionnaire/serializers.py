from rest_framework import serializers

from apps.common.serializers import UserResourceSerializer

from .models import Questionnaire, Question


class QuestionnaireSerializer(UserResourceSerializer):
    class Meta:
        model = Questionnaire
        fields = (
            'title',
        )


class QuestionSerializer(UserResourceSerializer):
    class Meta:
        model = Question
        fields = (
            # Parents
            'questionnaire',
            'group',
            # Question metadata
            'type',
            'name',
            'label',
            'hint',
        )

        """
        Validate
        - questionnaire
        - group
        """

    instance: Question

    def validate_questionnaire(self, questionnaire):
        if questionnaire.project_id != self.project.id:
            raise serializers.ValidationError('Invalid questionnaire')
        return questionnaire

    def validate(self, data):
        questionnaire = data.get(  # Required field
            'questionnaire',
            self.instance and self.instance.questionnaire
        )
        group = data.get('group')

        if group and group.questionnaire_id != questionnaire:
            raise serializers.ValidationError('Invalid group')
        return data
