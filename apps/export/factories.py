from factory.django import DjangoModelFactory

from .models import QuestionnaireExport


class QuestionnaireExportFactory(DjangoModelFactory):
    status = QuestionnaireExport.Status.PENDING
    xlsx_file = 'random-file-path/random-file.xlsx'
    xml_file = 'random-file-path/random-file.xml'

    class Meta:
        model = QuestionnaireExport
