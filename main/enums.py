import strawberry
import dataclasses

from apps.user.enums import enum_map as user_enum_map
from apps.common.enums import enum_map as common_enum_map
from apps.project.enums import enum_map as project_enum_map
from apps.qbank.enums import enum_map as qbank_enum_map
from apps.questionnaire.enums import enum_map as questionnaire_enum_map
from apps.export.enums import enum_map as export_enum_map


ENUM_TO_STRAWBERRY_ENUM_MAP: dict[str, type] = {
    **common_enum_map,
    **user_enum_map,
    **project_enum_map,
    **qbank_enum_map,
    **questionnaire_enum_map,
    **export_enum_map,
}


class AppEnumData():
    def __init__(self, enum):
        self.enum = enum

    @property
    def key(self):
        return self.enum

    @property
    def label(self):
        return str(self.enum.label)


def generate_app_enum_collection_data(name):
    return type(
        name,
        (),
        {
            field_name: [
                AppEnumData(e)
                for e in enum
            ]
            for field_name, enum in ENUM_TO_STRAWBERRY_ENUM_MAP.items()
        },
    )


AppEnumCollectionData = generate_app_enum_collection_data('AppEnumCollectionData')


def generate_type_for_enum(name, Enum):
    return strawberry.type(
        dataclasses.make_dataclass(
            f'AppEnumCollection{name}',
            [
                ('key', Enum),
                ('label', str),
            ]
        )
    )


def _enum_type(name, Enum):
    EnumType = generate_type_for_enum(name, Enum)

    @strawberry.field
    def _field() -> list[EnumType]:
        return [
            EnumType(
                key=e,
                label=e.label,
            )
            for e in Enum
        ]

    return list[EnumType], _field


def generate_type_for_enums():
    return strawberry.type(
        dataclasses.make_dataclass(
            'AppEnumCollection',
            (
                (enum_field_name, *_enum_type(enum_field_name, enum))
                for enum_field_name, enum in ENUM_TO_STRAWBERRY_ENUM_MAP.items()
            ),
        )
    )


AppEnumCollection = generate_type_for_enums()
