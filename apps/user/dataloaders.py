from asgiref.sync import sync_to_async
from django.utils.functional import cached_property
from strawberry.dataloader import DataLoader

from .models import User
from .types import UserType


def load_users(keys: list[str]) -> list[list[UserType]]:
    users_qs = User.objects.filter(id__in=keys)
    _map = {
        user.id: user
        for user in users_qs
    }
    return [_map[key] for key in keys]


class UserDataLoader():
    @cached_property
    def load_users(self) -> list[list[UserType]]:
        return DataLoader(load_fn=sync_to_async(load_users))
