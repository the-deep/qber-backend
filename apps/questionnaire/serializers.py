from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer

from utils.strawberry.serializers import IntegerIDField
from apps.common.serializers import (
    UserResourceSerializer,
    ProjectScopeSerializerMixin,
    TempClientIdMixin,
)

from apps.qbank.models import QuestionBank
from .models import (
    Questionnaire,
    Question,
    QuestionLeafGroup,
    Choice,
    ChoiceCollection,
)


class QuestionnaireSerializer(UserResourceSerializer):
    class Meta:
        model = Questionnaire
        fields = (
            'title',
            # Qber Metadata
            'priority_level',
            'enumerator_skill',
            'data_collection_method',
            'required_duration',
        )

    instance: Questionnaire

    def validate(self, data):
        qbank = QuestionBank.get_active()
        if qbank is None:
            raise serializers.ValidationError('No available Question Bank. Please ask admin to add one.')
        data['qbank'] = qbank
        return data

    def create(self, data):
        instance = super().create(data)
        # Create initial leaf groups using qbank
        QuestionLeafGroup.clone_from_qbank(
            instance,
            self.context['request'].user,
        )
        return instance


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


class QuestionLeafGroupOrderSerializer(serializers.Serializer):
    id = IntegerIDField(required=True)
    order = serializers.IntegerField(required=True)


class QuestionOrderSerializer(serializers.Serializer):
    id = IntegerIDField(required=True)
    order = serializers.IntegerField(required=True)


class QuestionSerializer(UserResourceSerializer):
    class Meta:
        model = Question
        fields = (
            # Parents
            'questionnaire',
            'leaf_group',
            # Qber Metadata
            'priority_level',
            'enumerator_skill',
            'data_collection_method',
            'required_duration',
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
        leaf_group = data.get('leaf_group', self.instance and self.instance.leaf_group)

        errors = []
        if (
            'leaf_group' in data and
            leaf_group.questionnaire_id != questionnaire.id
        ):
            errors.append('Invalid group')
        if (
            'choice_collection' in data and
            choice_collection and
            choice_collection.questionnaire_id != questionnaire.id
        ):
            errors.append('Invalid choices')
        if (
            'type' in data and
            _type in Question.FIELDS_WITH_CHOICE_COLLECTION and
            choice_collection is None
        ):
            errors.append(f'Choices are required for {_type}')

        if errors:
            raise serializers.ValidationError(errors)
        return data
