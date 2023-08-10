from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer

from utils.strawberry.serializers import IntegerIDField
from apps.common.serializers import (
    UserResourceSerializer,
    ProjectScopeSerializerMixin,
    TempClientIdMixin,
)

from .models import (
    Questionnaire,
    Question,
    QuestionGroup,
    Choice,
    ChoiceCollection,
)


class QuestionnaireSerializer(UserResourceSerializer):
    class Meta:
        model = Questionnaire
        fields = (
            'title',
        )

    instance: Questionnaire


class QuestionGroupSerializer(UserResourceSerializer):
    class Meta:
        model = QuestionGroup
        fields = (
            # Parents
            'questionnaire',
            'parent',
            # Question Group metadata
            'name',
            'label',
            'relevant',
        )

    instance: QuestionGroup

    def validate_questionnaire(self, questionnaire):
        if questionnaire.project_id != self.project.id:
            raise serializers.ValidationError('Invalid questionnaire')
        return questionnaire

    def validate(self, data):
        questionnaire = data.get(  # Required field
            'questionnaire',
            self.instance and self.instance.questionnaire
        )
        parent = data.get('parent')

        if parent and parent.questionnaire_id != questionnaire:
            raise serializers.ValidationError('Invalid parent question group')
        return data


class QuestionChoiceSerializer(TempClientIdMixin, ProjectScopeSerializerMixin, serializers.ModelSerializer):
    id = IntegerIDField(required=False)

    class Meta:
        model = Choice
        fields = (
            'id',
            'client_id',
            # Metadata
            'name',
            'label',
            # 'geometry',
        )

    # TODO: For `id` make sure it is empty for create and for update it belongs to the choiceCollection
    instance: ChoiceCollection

    def validate_collection(self, choice_collection):
        if choice_collection.questionnaire.project_id != self.project.id:
            raise serializers.ValidationError('Invalid choice collection')
        return choice_collection


class QuestionChoiceCollectionSerializer(UserResourceSerializer, WritableNestedModelSerializer):
    class Meta:
        model = ChoiceCollection
        fields = (
            # Parents
            'questionnaire',
            # Metadata
            'name',
            'label',
            'choices',
        )

    instance: ChoiceCollection

    choices = QuestionChoiceSerializer(many=True, source='choice_set')

    def validate_questionnaire(self, questionnaire):
        if questionnaire.project_id != self.project.id:
            raise serializers.ValidationError('Invalid questionnaire')
        return questionnaire


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
