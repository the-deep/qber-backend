import typing
from collections import defaultdict

import pandas as pd
from pyxform.xls2xform import xls2xform_convert

from apps.export.models import QuestionnaireExport
from apps.questionnaire.models import (
    QuestionLeafGroup,
    Question,
    Questionnaire,
    ChoiceCollection,
    Choice
)


class UnknownQuestionLeafGroupType(Exception):
    def __init__(self, leaf_group):
        self.message = f'Unknown leaf group type: {leaf_group.get_type_display()}'
        super().__init__(self.message)


class XlsQuestionType:
    @staticmethod
    def get_select_one(question):
        name = f'select_one {question.choice_collection.name}'
        if question.is_or_other:
            return f'{name} or_other'
        return name

    @staticmethod
    def get_select_multiple(question):
        name = f'select_multiple {question.choice_collection.name}'
        if question.is_or_other:
            return f'{name} or_other'
        return name

    MAP: dict[Question.Type, str | typing.Callable[[Question], str]] = {
        Question.Type.INTEGER: 'integer',
        Question.Type.DECIMAL: 'decimal',
        Question.Type.TEXT: 'text',
        Question.Type.SELECT_ONE: get_select_one,
        Question.Type.SELECT_MULTIPLE: get_select_multiple,
        Question.Type.RANK: lambda q: f'rank {q.choice_collection.name}',
        Question.Type.RANGE: 'range',
        Question.Type.NOTE: 'note',
        Question.Type.DATE: 'date',
        Question.Type.TIME: 'time',
        Question.Type.DATETIME: 'datetime',
        Question.Type.IMAGE: 'image',
        Question.Type.AUDIO: 'audio',
        Question.Type.VIDEO: 'video',
        Question.Type.FILE: 'file',
        Question.Type.BARCODE: 'barcode',
        Question.Type.ACKNOWLEDGE: 'acknowledge',
    }

    @classmethod
    def get_name(cls, question: Question) -> str:
        _name = cls.MAP[question.type]
        if callable(_name):
            return _name(question)
        return _name


class XlsSheet:
    BOOLEAN_MAP = {
        None: '',
        True: 'true',
        False: 'false',
    }

    SURVEY_HEADERS = (
        'name',
        'type',
        'label',
        'hint',
        'default',
        'guidance_hint',
        'trigger',
        'readonly',
        'required',
        'required_message',
        'relevant',
        'constraint',
        'constraint_message',
        'appearance',
        'calculation',
        'parameters',
        'choice_filter',
        'image',
        'video',
    )

    @classmethod
    def get_survey_dict(cls, question: Question):
        return {
            'name': question.name,
            'type': XlsQuestionType.get_name(question),
            'label': question.label,
            'hint': question.hint,
            'default': question.default,
            'guidance_hint': question.guidance_hint,
            'trigger': question.trigger,
            'readonly': question.readonly,
            'required': cls.BOOLEAN_MAP[question.required],
            'required_message': question.required_message,
            'relevant': question.relevant,
            'constraint': question.constraint,
            'constraint_message': question.constraint_message,
            'appearance': question.appearance,
            'calculation': question.calculation,
            'parameters': question.parameters,
            'choice_filter': question.choice_filter,
            'image': question.image,
            'video': question.video,
        }

    SURVEY_END_GROUP_ROW = {
        'type': 'end group'
    }

    @classmethod
    def get_survey_raw_group_dict(cls, name: str, label: str):
        return {
            'name': name,
            'type': 'begin group',
            'label': label,
        }

    @classmethod
    def get_survey_group_dict(cls, leaf_group: QuestionLeafGroup):
        label = 'N/A'
        if leaf_group.type == QuestionLeafGroup.Type.MATRIX_1D:
            label = leaf_group.get_category_2_display()
        elif leaf_group.type == QuestionLeafGroup.Type.MATRIX_2D:
            label = leaf_group.get_category_4_display()
        else:
            raise UnknownQuestionLeafGroupType(leaf_group)
        return {
            'name': leaf_group.name,
            'type': 'begin group',
            'label': label,
            'relevant': leaf_group.relevant,
        }

    CHOICE_HEADERS = (
        'list name',
        'name',
        'label',
    )

    @staticmethod
    def get_choice_dict(choice_collection: ChoiceCollection, choice: Choice):
        return {
            'list name': choice_collection.name,
            'name': choice.name,
            'label': choice.label,
            # 'geometry': choice.geometry,
            # 'label::[]': '',
            # 'media': '',
            # '[filter_category_name]': '',
        }

    SETTINGS_HEADERS = (
        'form_title',
        'form_id',
        'version',
    )

    @staticmethod
    def get_settings_dict(questionnaire: Questionnaire):
        return {
            'form_title': questionnaire.title,
            'form_id': questionnaire.id,
            # 'version': '',
            # 'instance_name': '',
            # 'default_language': '',
        }


def generate_groups_tree(leaf_groups: list[QuestionLeafGroup]):
    """
    Borrowed from client side
    # TODO: Refactor
    # Test
    """
    def transform_options_by_category(_leaf_groups: list[QuestionLeafGroup]):
        result = []
        for leaf_group in _leaf_groups:
            result.append({
                'id': leaf_group.id,
                'type': leaf_group.type,
                'categories': [
                    {
                        'key': category,
                        'label': label,
                    }
                    for category, label in [
                        (leaf_group.category_1, leaf_group.get_category_1_display()),
                        (leaf_group.category_2, leaf_group.get_category_2_display()),
                        (leaf_group.category_3, leaf_group.get_category_3_display()),
                        (leaf_group.category_4, leaf_group.get_category_4_display()),
                    ]
                    if category
                ]
            })
        return result

    def list_to_group_list(array, key_selector, modifier):
        acc = {}
        for elem in array:
            key = key_selector(elem)
            value = modifier(elem)
            group = acc.get(key)
            if group:
                group.append(value)
            else:
                acc[key] = [value]
        return acc

    def map_to_list(obj, modifier):
        acc = []
        for key in obj.keys():
            elem = obj[key]
            acc.append(
                modifier(elem, key)
            )
        return acc

    def get_nodes(group_nodes, parent_keys):
        non_leaf_nodes = [
            node
            for node in group_nodes
            if len(node['categories']) > 1
        ]

        grouped_non_leaf_nodes = list_to_group_list(
            non_leaf_nodes,
            lambda group_item: group_item['categories'][0]['key'],
            lambda group_item: ({
                'categories': group_item['categories'][1:],
                'parent_label': group_item['categories'][0]['label'],
                'parent_key': group_item['categories'][0]['key'],
                'type': group_item['type'],
                'id': group_item['id'],
            }),
        )

        non_leaf_nodes_response = map_to_list(
            grouped_non_leaf_nodes,
            lambda item, key: {
                'key': key,
                'label': item[0]['parent_label'],
                'parent_keys': [
                    *parent_keys,
                    item[0]['parent_key'],
                ],
                'nodes': get_nodes(
                    item,
                    [
                        *parent_keys,
                        item[0]['parent_key'],
                    ],
                ),
            },
        )

        leaf_nodes = [
            node
            for node in group_nodes
            if len(node['categories']) <= 1
        ]
        leaf_nodes_response = [
            {
                'key': item['categories'][0]['key'],
                'label': item['categories'][0]['label'],
                'parent_keys': [
                    *parent_keys,
                    item['categories'][0]['key'],
                ],
                'leafNode': True,
                'id': item['id'],
            }
            for item in leaf_nodes
        ]

        return [
            *leaf_nodes_response,
            *non_leaf_nodes_response,
        ]

    groups_by_category = transform_options_by_category(leaf_groups)
    return get_nodes(groups_by_category, [])


def generate_data(questionnaire: Questionnaire) -> tuple[dict, dict, dict]:
    leaf_groups = list(
        QuestionLeafGroup.objects.filter(
            questionnaire=questionnaire,
            is_hidden=False,
        ).order_by('order')
    )

    # Surveys -- Questions and Groups
    choice_collections = {}
    leaf_groups_collections = defaultdict(list)
    # -- Leaf Groups + Questions
    for leaf_group in leaf_groups:
        questions_qs = Question.objects.filter(
            leaf_group=leaf_group,
            is_hidden=False,
        ).order_by('order')
        # Group begin row
        leaf_groups_collections[leaf_group.pk].append(XlsSheet.get_survey_group_dict(leaf_group))
        for question in questions_qs:
            # Question row
            leaf_groups_collections[leaf_group.pk].append(XlsSheet.get_survey_dict(question))
            # Collect used choices
            if question.choice_collection_id and question.choice_collection_id not in choice_collections:
                choice_collections[question.choice_collection_id] = question.choice_collection
        # Group end row
        leaf_groups_collections[leaf_group.pk].append(XlsSheet.SURVEY_END_GROUP_ROW)

    # Groups TOC
    survey_list = []

    def _add_to_survey_list(nodes, _list, parent_key=None):
        for node in nodes:
            _nodes = node.get('nodes')
            if _nodes is not None:
                # We need to add group for non-leaf nodes only
                _node_key = f"category__{node['key']}"
                if parent_key:
                    _node_key = f"{parent_key}__{_node_key}"
                _list.append(
                    XlsSheet.get_survey_raw_group_dict(
                        _node_key,
                        node['label'],
                    )
                )
                _add_to_survey_list(_nodes, _list, parent_key=_node_key)
                _list.append(XlsSheet.SURVEY_END_GROUP_ROW)
            else:
                _list.extend(leaf_groups_collections[node['id']])

    groups_tree = generate_groups_tree(leaf_groups)
    _add_to_survey_list(groups_tree, survey_list)

    # Choices
    choices_list = []
    for choice_collection in choice_collections.values():
        for choice in choice_collection.choice_set.all():
            choices_list.append(XlsSheet.get_choice_dict(choice_collection, choice))

    return {
        # Survey
        'headers': XlsSheet.SURVEY_HEADERS,
        'values': survey_list
    }, {
        # Choice
        'headers': XlsSheet.CHOICE_HEADERS,
        'values': choices_list,
    }, {
        # Settings
        'headers': XlsSheet.SETTINGS_HEADERS,
        'values': [XlsSheet.get_settings_dict(questionnaire)],
    }


def export(
    export: QuestionnaireExport,
    temp_xlsx_file: typing.IO[typing.Any],
    temp_xml_file: typing.IO[typing.Any],
) -> None:
    questionnaire = export.questionnaire
    surveys, choices, settings = generate_data(questionnaire)
    survey_df = pd.DataFrame.from_records(surveys['values'])
    choices_df = pd.DataFrame.from_records(choices['values'])
    settings_df = pd.DataFrame.from_records(settings['values'])
    # Generate XLSX
    with pd.ExcelWriter(
        temp_xlsx_file,
        engine='openpyxl'
    ) as writer:  # pyright: ignore [reportGeneralTypeIssues]
        survey_df.to_excel(writer, sheet_name='survey')
        choices_df.to_excel(writer, sheet_name='choices')
        settings_df.to_excel(writer, sheet_name='settings')
    # Generate XML
    temp_xlsx_file.seek(0)
    xls2xform_convert(
        temp_xlsx_file.name,
        temp_xml_file.name,
        # NOTE: Need to install java as dependencies for validation, Instead we use standalone enketo for that
        validate=False,
        enketo=False,
    )
