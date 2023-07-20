import factory
from factory.django import DjangoModelFactory

from .models import Project


class ProjectFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'Project-{n}')

    class Meta:
        model = Project
