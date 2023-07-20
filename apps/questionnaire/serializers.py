from apps.common.serializers import UserResourceSerializer
from .models import Questionnaire


class QuestionnaireSerializer(UserResourceSerializer):
    class Meta:
        model = Questionnaire
        fields = (
            'title',
        )
