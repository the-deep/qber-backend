from factory.django import DjangoModelFactory

from .models import GlobalPermission


class GlobalPermissionFactory(DjangoModelFactory):
    class Meta:
        model = GlobalPermission
