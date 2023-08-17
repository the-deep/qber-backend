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

        if parent and parent.questionnaire_id != questionnaire.id:
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
            'choice_collection',
            # XLSForm fields
            'default',
            'guidance_hint',
            'trigger',
            'readonly',
            'required',
            'required_message',
            'relevant',
            'constraint',
            'appearance',
            'calculation',
            'parameters',
            'choice_filter',
            'image',
            'video',
            'is_or_other',
            'or_other_label',
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
        _type = data.get('type', self.instance and self.instance.type)
        choice_collection = data.get('choice_collection', self.instance and self.instance.choice_collection)
        group = data.get('group', self.instance and self.instance.group)

        errors = []
        if 'group' in data and group and group.questionnaire_id != questionnaire.id:
            errors.append('Invalid group')
        if 'choice_collection' in data and choice_collection and choice_collection.questionnaire_id != questionnaire.id:
            errors.append('Invalid choices')
        if 'type' in data and _type in Question.FIELDS_WITH_CHOICE_COLLECTION and choice_collection is None:
            errors.append(f'Choices are required for {_type}')

        if errors:
            raise serializers.ValidationError(errors)
        return data
