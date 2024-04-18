from asgiref.sync import sync_to_async
from django.utils.functional import cached_property
from strawberry.dataloader import DataLoader

from .models import Project, ProjectMembership
from .types import ProjectPermissionTypeEnum


def load_user_permissions(keys: list[tuple[int, int]]) -> list[list[ProjectPermissionTypeEnum]]:
    # keys: tuple(user id, Project IDs)
    user_ids = list(set([user_id for user_id, _ in keys]))
    project_ids = list(set([project_id for _, project_id in keys]))
    qs = ProjectMembership.objects.filter(
        member__in=user_ids,
        project__in=project_ids,
    ).values_list('member_id', 'project_id', 'role')
    _map = {
        (member_id, project_id): Project.get_permissions().get(role, [])
        for member_id, project_id, role in qs
    }
    return [_map.get(key, []) for key in keys]


class ProjectDataLoader():
    @cached_property
    def load_user_permissions(self) -> list[list[ProjectPermissionTypeEnum]]:
        return DataLoader(load_fn=sync_to_async(load_user_permissions))
