from django.utils.functional import cached_property

from apps.questionnaire.dataloaders import QuestionnaireDataLoader
from apps.qbank.dataloaders import QBankDataLoader
from apps.project.dataloaders import ProjectDataLoader
from apps.user.dataloaders import UserDataLoader


class GlobalDataLoader:

    @cached_property
    def questionnaire(self):
        return QuestionnaireDataLoader()

    @cached_property
    def user(self):
        return UserDataLoader()

    @cached_property
    def qbank(self):
        return QBankDataLoader()

    @cached_property
    def project(self):
        return ProjectDataLoader()
