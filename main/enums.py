from apps.user.enums import enum_map as user_enum_map
from apps.project.enums import enum_map as project_enum_map
from apps.questionnaire.enums import enum_map as questionnaire_enum_map


ENUM_TO_STRAWBERRY_ENUM_MAP = {
    **user_enum_map,
    **project_enum_map,
    **questionnaire_enum_map,
}
