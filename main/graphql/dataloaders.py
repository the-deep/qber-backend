from django.utils.functional import cached_property

from apps.questionnaire.dataloaders import QuestionnaireDataLoader
from apps.user.dataloaders import UserDataLoader


class GlobalDataLoader:

    @cached_property
    def questionnaire(self):
        return QuestionnaireDataLoader()

    @cached_property
    def user(self):
        return UserDataLoader()
