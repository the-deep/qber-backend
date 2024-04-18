import random

from main.tests import TestCase

from apps.user.factories import UserFactory
from apps.project.factories import ProjectFactory
from apps.questionnaire.models import Question
from apps.export.factories import QuestionnaireExportFactory
from apps.export.tasks import export_task
from apps.export.models import QuestionnaireExport
from apps.qbank.factories import QuestionBankFactory
from apps.questionnaire.factories import (
    QuestionnaireFactory,
    QuestionFactory,
    QuestionLeafGroupFactory,
    ChoiceCollectionFactory,
    ChoiceFactory,
)


class TestExportTaskQuery(TestCase):
    def test_questionnaire_export(self):
        user = UserFactory.create()
        user_resource_params = {'created_by': user, 'modified_by': user}
        qbank = QuestionBankFactory.create(**user_resource_params)
        project = ProjectFactory.create(**user_resource_params)
        project.add_member(user)
        # TODO: Add more cases
        q1, _ = QuestionnaireFactory.create_batch(2, project=project, **user_resource_params, qbank=qbank)
        # For q1 only
        choice_collections = ChoiceCollectionFactory.create_batch(
            2,
            **user_resource_params,
            questionnaire=q1,
            label='[Choices] Gender',
        )
        ChoiceFactory.create_batch(3, collection=choice_collections[0])
        ChoiceFactory.create_batch(5, collection=choice_collections[1])
        groups = QuestionLeafGroupFactory.static_generator(20, **user_resource_params, questionnaire=q1)
        for group in groups:
            for type_, _ in Question.Type.choices:
                question_params = {**user_resource_params}
                if type_ in Question.FIELDS_WITH_CHOICE_COLLECTION:
                    question_params['choice_collection'] = random.choice(choice_collections)
                QuestionFactory.create_batch(2, **question_params, leaf_group=group, type=type_)
                QuestionFactory.create_batch(3, **question_params, leaf_group=group, type=type_)
                QuestionFactory.create_batch(5, **question_params, leaf_group=group, type=type_)
        export = QuestionnaireExportFactory.create(exported_by=user, questionnaire=q1)

        export_task(export.id)
        export.refresh_from_db()
        assert export.status == QuestionnaireExport.Status.SUCCESS
