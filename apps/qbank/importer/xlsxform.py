import logging

from django.core.files.temp import NamedTemporaryFile
from django.conf import settings
from django.db import transaction
from pyxform.xls2json import parse_file_to_json

from apps.qbank.base_models import BaseQuestion, BaseQuestionLeafGroup
from apps.qbank.models import (
    QBChoice,
    QBChoiceCollection,
    QBQuestion,
    QuestionBank,
    QBLeafGroup,
)

logger = logging.getLogger(__name__)


class Parser:
    @staticmethod
    def no_op(value):
        """
        No operation, just return argument
        """
        return value

    @staticmethod
    def label(label_data):
        if label := label_data.get('default'):
            return label
        return list(label_data.values())[0]

    @staticmethod
    def priority_level(value):
        if value is None:
            return
        return QBQuestion.PriorityLevel[
            value.upper().replace('PRIORITY', '').strip().replace(' ', '_')
        ]

    @staticmethod
    def enumerator_skill(value):
        if value is None:
            return
        _value = value.upper()
        override = {
            'MEDIUM': QBQuestion.EnumeratorSkill.INTERMEDIATE,
        }
        return override.get(_value) or QBQuestion.EnumeratorSkill[
            _value.strip().replace(' ', '_')
        ]

    @staticmethod
    def data_collection_method(value):
        if value is None:
            return
        _value = value.upper()
        override = {
            'DIRECT OBSERVATION': QBQuestion.DataCollectionMethod.DIRECT,
            '1-ON-1 INTERVIEWS': QBQuestion.DataCollectionMethod.ONE_ON_ONE_INTERVIEW,
        }
        return override.get(_value) or QBQuestion.DataCollectionMethod[
            _value.strip().replace(' ', '_').replace('-', '_')
        ]

    @staticmethod
    def category_enum(raw):
        if raw is None:
            return raw
        for replace, replace_with in [
            ('-', '_'),
            ('&', 'AND'),
            ('(', ''),
            (')', ''),
        ]:
            raw = raw.replace(replace, replace_with)
        return raw.strip().replace(' ', '_').upper()


class XlsFormImport:
    BASIC_QUESTION_TYPE_MAP: dict[str, BaseQuestion.Type] = {
        'integer': BaseQuestion.Type.INTEGER,
        'decimal': BaseQuestion.Type.DECIMAL,
        'text': BaseQuestion.Type.TEXT,
        'range': BaseQuestion.Type.RANGE,
        'note': BaseQuestion.Type.NOTE,
        'date': BaseQuestion.Type.DATE,
        'time': BaseQuestion.Type.TIME,
        'datetime': BaseQuestion.Type.DATETIME,
        'image': BaseQuestion.Type.IMAGE,
        'audio': BaseQuestion.Type.AUDIO,
        'video': BaseQuestion.Type.VIDEO,
        'file': BaseQuestion.Type.FILE,
        'barcode': BaseQuestion.Type.BARCODE,
        'acknowledge': BaseQuestion.Type.ACKNOWLEDGE,
        'select one': BaseQuestion.Type.SELECT_ONE,
        'select multiple': BaseQuestion.Type.SELECT_MULTIPLE,
        'select all that apply': BaseQuestion.Type.SELECT_MULTIPLE,
        'rank': BaseQuestion.Type.RANK,
    }

    CUSTOM_CATEGORY_MAP = {
        BaseQuestionLeafGroup.Category1: {
            Parser.category_enum(category.label): category
            for category in BaseQuestionLeafGroup.Category1
        },
        BaseQuestionLeafGroup.Category2: {
            Parser.category_enum(category.label): category
            for category in BaseQuestionLeafGroup.Category2
        },
        BaseQuestionLeafGroup.Category3: {
            Parser.category_enum(category.label): category
            for category in BaseQuestionLeafGroup.Category3
        },
        BaseQuestionLeafGroup.Category4: {
            Parser.category_enum(category.label): category
            for category in BaseQuestionLeafGroup.Category4
        },
    }

    def __init__(self, qbank: QuestionBank):
        self.qbank = qbank
        self.choice_collection_map: dict[str, QBChoiceCollection] = {}
        self.leaf_group_map: dict[tuple[str, str, str | None, str | None], QBLeafGroup] = {}
        self.questions: list[QBQuestion] = []
        self.errors: list[str] = []

    def log_error(self, error_msg):
        self.errors.append(error_msg)

    def qber_debug_index(self, data):
        index = data.get('qber-debug-index', 'N/A')
        return f'qber-debug-index: {index} -- '

    def get_choice_collection(self, data) -> QBChoiceCollection:
        name = data['list_name']
        if choice_collection := self.choice_collection_map.get(name):
            return choice_collection
        new_choice_collection = QBChoiceCollection.objects.create(
            qbank=self.qbank,
            name=name,
            label=name,
        )
        new_choices = []
        for choice in data['choices']:
            new_choices.append(
                QBChoice(
                    collection=new_choice_collection,
                    name=choice['name'],
                    label=Parser.label(choice['label']),
                )
            )
        QBChoice.objects.bulk_create(new_choices)
        self.choice_collection_map[name] = new_choice_collection
        return new_choice_collection

    def get_leaf_group(self, data) -> QBLeafGroup | None:
        pillar = Parser.category_enum(data.get('Pillar'))
        sub_pillar = Parser.category_enum(data.get('Sub pillar'))
        sector = Parser.category_enum(data.get('Sector'))
        sub_sector = Parser.category_enum(data.get('Sub sector'))
        if pillar is None or sub_pillar is None:
            self.log_error(f'{self.qber_debug_index(data)} Skipping as {pillar=} or {sub_pillar=} is None')
            return
        if all([sector, sub_sector]) != any([sector, sub_sector]):
            self.log_error(f'{self.qber_debug_index(data)} Skipping as {sector=} is None for {sub_sector=} is None')
            return
        try:
            _categories = [None, None, None, None]
            for _index, (CategoryN, raw_value) in enumerate([
                (BaseQuestionLeafGroup.Category1, pillar),
                (BaseQuestionLeafGroup.Category2, sub_pillar),
                (BaseQuestionLeafGroup.Category3, sector),
                (BaseQuestionLeafGroup.Category4, sub_sector),
            ]):
                if raw_value is None:
                    continue

                _categories[_index] = (
                    self.CUSTOM_CATEGORY_MAP[CategoryN].get(raw_value) or
                    CategoryN[raw_value].value
                )
            categories: tuple[str, str, str | None, str | None] = tuple(_categories)
            del _categories
        except (KeyError, ValueError):
            _category_n = locals().get('CategoryN') and locals().get('CategoryN').__name__
            _raw_value = locals().get('raw_value')
            self.log_error(
                f'{self.qber_debug_index(data)} Failed to parse category '
                f'{_category_n} for given value "{_raw_value}"'
            )
            return
        if categories not in self.leaf_group_map:
            self.log_error(f'Invalid categories: {categories}')
            return
        return self.leaf_group_map[categories]

    def create_leaf_group(self):
        # Matrix 1D
        leaf_groups = [
            QBLeafGroup(
                qbank=self.qbank,
                name='-'.join([str(c) for c in [c1, c2] if c is not None]),
                type=QBLeafGroup.Type.MATRIX_1D,
                category_1=c1,
                category_2=c2,
            )
            for c1, c2_list in QBLeafGroup.TYPE_CATEGORY_MAP[QBLeafGroup.Type.MATRIX_1D].items()
            for c2 in c2_list
        ]
        # Matrix 2D
        leaf_groups.extend([
            QBLeafGroup(
                qbank=self.qbank,
                name='-'.join([str(c) for c in [c1, c2, c3, c4] if c is not None]),
                type=QBLeafGroup.Type.MATRIX_2D,
                category_1=c1,
                category_2=c2,
                category_3=c3,
                category_4=c4,
            )
            for c1, c2_list in QBLeafGroup.TYPE_CATEGORY_MAP[QBLeafGroup.Type.MATRIX_2D]['rows'].items()
            for c2 in c2_list
            for c3, c4_list in QBLeafGroup.TYPE_CATEGORY_MAP[QBLeafGroup.Type.MATRIX_2D]['columns'].items()
            for c4 in c4_list
        ])
        QBLeafGroup.objects.bulk_create(leaf_groups)
        return {
            (
                lg.category_1,
                lg.category_2,
                lg.category_3,
                lg.category_4,
            ): lg
            for lg in QBLeafGroup.objects.filter(qbank=self.qbank).all()
        }

    def process_each(self, data):
        _type = data['type'].lower()

        # Groups (Ignoring groups for now as we have our own grouping using custom column)
        if _type in ['survey', 'group']:
            children_list = data.get('children') or []
            if children_list:
                for child in children_list:
                    self.process_each(child)
            logger.info(f'{self.qber_debug_index(data)} Survey and groups are skipped')
            return

        # TODO: Throw error if not found
        if (_internal_type := self.BASIC_QUESTION_TYPE_MAP.get(_type)) is None:
            self.log_error(f'{self.qber_debug_index(data)} No type found {_type=}')
            return

        kwargs = {
            'qbank': self.qbank,
            'type': _internal_type,
        }
        if _internal_type in QBQuestion.FIELDS_WITH_CHOICE_COLLECTION:
            kwargs['choice_collection'] = self.get_choice_collection(data)

        if (leaf_group := self.get_leaf_group(data)) is None:
            return
        kwargs['leaf_group'] = leaf_group

        # Question fields
        for internal_field, data_key, parser in [
            ('label', 'label', Parser.label),
            ('name', 'name', Parser.no_op),
            ('hint', 'hint', Parser.no_op),
            ('required', 'required', Parser.no_op),
            ('appearance', 'appearance', Parser.no_op),
            ('relevant', 'relevant', Parser.no_op),
            ('constraint', 'constraint', Parser.no_op),
            ('constraint_message', 'constraint_message', Parser.no_op),
            # Qber Metadata
            ('priority_level', 'Priority level', Parser.priority_level),
            ('enumerator_skill', 'Enumerator skill level required', Parser.enumerator_skill),
            ('data_collection_method', 'Data Collection Methods', Parser.data_collection_method),
        ]:
            _value = parser(data.get(data_key))
            if _value:
                kwargs[internal_field] = _value

        if required_duration_raw := data.get('Time(min)'):
            try:
                kwargs['required_duration'] = int(float(required_duration_raw) * 60)
            except ValueError:
                logger.error('Failed to parse required_duration', exc_info=True)
                self.log_error(f'{self.qber_debug_index(data)} Time(min) should be float value: {required_duration_raw}')
                pass

        self.questions.append(
            QBQuestion(
                **kwargs
            )
        )

    @staticmethod
    def validate_xlsform(file):
        with NamedTemporaryFile(
            dir=settings.TEMP_FILE_DIR,
            delete=True,
            suffix='.xlsx',
        ) as temp_xlsx_file:
            file.seek(0)
            temp_xlsx_file.write(file.read())
            return parse_file_to_json(temp_xlsx_file.name)

    @transaction.atomic
    def process(self):
        # TODO: Run only once
        self.choice_collection_map = {}
        self.leaf_group_map = self.create_leaf_group()
        self.questions = []
        self.errors = []
        self.process_each(self.validate_xlsform(self.qbank.import_file))
        QBQuestion.objects.bulk_create(self.questions)
        if self.errors:
            print(f'----------------------------- ERRORS ({len(self.errors)}) -----------------------------')
            for error in self.errors:
                print(error)
