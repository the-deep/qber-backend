from factory.django import DjangoModelFactory

from .models import QuestionnaireExport


class QuestionnaireExportFactory(DjangoModelFactory):
    type = QuestionnaireExport.Type.XLSFORM
    status = QuestionnaireExport.Status.PENDING
    file = 'random-file-path'

    class Meta:
        model = QuestionnaireExport
