from rest_framework import serializers

from utils.strawberry.serializers import IntegerIDField
from apps.common.serializers import UserResourceSerializer, TempClientIdMixin

from .models import Project, ProjectMembership


class ProjectSerializer(UserResourceSerializer):
    class Meta:
        model = Project
        fields = (
            'title',
        )

    def create(self, data):
        project = super().create(data)
        # Create a membership for the user
        ProjectMembership.objects.create(
            project=project,
            member=project.created_by,
            role=ProjectMembership.Role.ADMIN,
        )
        return project


class ProjectMembershipBulkSerializer(TempClientIdMixin, UserResourceSerializer):
    # NOTE: Required by ModelMutation
    id = IntegerIDField(required=False)

    class Meta:
        model = ProjectMembership
        fields = (
            'id',
            'client_id',
            'member',
            'role',
        )

    def validate(self, data):
        # Check if already exists
        if 'member' in data:
            qs = ProjectMembership.objects.filter(
                project=self.project,
                member=data['member']
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('Membership already exists.')
        return data
