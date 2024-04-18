from main.tests import TestCase

from apps.project.models import Project, ProjectMembership
from apps.user.factories import UserFactory
from apps.project.factories import ProjectFactory


class TestProjectMutation(TestCase):
    class Mutation:
        ProjectCreate = '''
            mutation MyMutation($data: ProjectCreateInput!) {
              private {
                createProject(data: $data) {
                  ok
                  errors
                  result {
                    id
                    title
                    members {
                      count
                      items {
                        id
                        memberId
                        addedById
                        role
                        joinedAt
                      }
                    }
                    modifiedAt
                    createdAt
                  }
                }
              }
            }
        '''

        ProjectUpdate = '''
            mutation MyMutation($project_id: ID!, $data: ProjectUpdateInput!) {
              private {
                projectScope(pk: $project_id) {
                  updateProject(data: $data) {
                    ok
                    errors
                    result {
                      id
                      title
                      members {
                        count
                        items {
                          id
                          memberId
                          addedById
                          role
                          joinedAt
                        }
                      }
                      modifiedAt
                      createdAt
                    }
                  }
                }
              }
            }
        '''

        ProjectMembershipBulkUpdate = '''
            mutation MyMutation(
                $project_id: ID!
                $items: [ProjectMembershipUpdateInput!],
                $delete_ids: [ID!]
            ) {
              private {
                projectScope(pk: $project_id) {
                  updateMemberships(
                    items: $items
                    deleteIds: $delete_ids
                  ) {
                    errors
                    results {
                      id
                      memberId
                      role
                      clientId
                    }
                    deleted {
                      id
                      memberId
                      role
                      clientId
                    }
                  }
                }
              }
            }
        '''

        ProjectMembershipLeave = '''
            mutation MyMutation($project_id: ID!, $confirm_password: String!) {
              private {
                projectScope(pk: $project_id) {
                  leaveProject(confirmPassword: $confirm_password) {
                    ok
                    errors
                  }
                }
              }
            }
        '''

    def test_create_project(self):
        user = UserFactory.create()

        project_count = Project.objects.count()
        # Without login
        variables = {'data': {'title': 'Project 1'}}
        content = self.query_check(self.Mutation.ProjectCreate, variables=variables, assert_errors=True)
        assert content['data'] is None
        # No change
        assert project_count == Project.objects.count()

        # With login
        self.force_login(user)
        content = self.query_check(self.Mutation.ProjectCreate, variables=variables)
        assert project_count + 1 == Project.objects.count()
        latest_project = Project.objects.last()
        content_response = content['data']['private']['createProject']
        assert content_response['ok'] is True
        self.assertEqual(content_response['result']['id'], self.gID(latest_project.id), content)
        self.assertEqual(content_response['result']['title'], latest_project.title, content)

    def test_update_project(self):
        user = UserFactory.create()
        # NOTE: created_by/modified_by != membership
        project = ProjectFactory.create(created_by=user, modified_by=user)
        project_count = Project.objects.count()

        # Without login
        project_title = project.title
        variables = {
            'project_id': project.id,
            'data': {
                'title': project.title + 'Updated',
            }
        }
        content = self.query_check(self.Mutation.ProjectUpdate, variables=variables, assert_errors=True)
        assert content['data'] is None
        project.refresh_from_db()
        assert project.title == project_title

        self.force_login(user)
        for role, has_access in [
            # With login - No membership
            (None, False),
            # With login - Normal membership
            (ProjectMembership.Role.MEMBER, False),
            # With login - Admin membership
            (ProjectMembership.Role.ADMIN, True),
        ]:
            if role is not None:
                project.add_member(user, role=role)
            content = self.query_check(self.Mutation.ProjectUpdate, variables=variables)
            project.refresh_from_db()
            if not has_access:
                if role is None:
                    assert content['data']['private']['projectScope'] is None
                else:
                    content_response = content['data']['private']['projectScope']['updateProject']
                    assert content_response['ok'] is False, content
                assert project.title == project_title
                continue

            content_response = content['data']['private']['projectScope']['updateProject']
            assert content_response['ok'] is True, content_response
            self.assertEqual(content_response['result']['id'], self.gID(project.id), content)
            self.assertEqual(content_response['result']['title'], variables['data']['title'], content)
            assert project.title != project_title

        # No change in project count
        assert project_count == Project.objects.count()

    def test_update_project_membership(self):
        user, *users = UserFactory.create_batch(6)
        # NOTE: created_by/modified_by != membership
        project = ProjectFactory.create(created_by=user, modified_by=user)

        memberships = []
        for _user in users[:4]:
            memberships.append(
                project.add_member(_user)
            )

        to_be_member_user = users[-1]
        to_be_modified_memberships = memberships[:2]
        to_be_deleted_memberships = memberships[2:5]
        # Without login
        variables = {
            'project_id': project.id,
            'items': [
                # Two new
                {  # Invalid - User has already membership
                    'clientId': 'client-new-id',
                    'member': memberships[0].member_id,
                    'role': self.genum(ProjectMembership.Role.MEMBER),
                },
                {  # Valid
                    'clientId': 'client-new-id',
                    'member': self.gID(to_be_member_user.id),
                    'role': self.genum(ProjectMembership.Role.MEMBER),
                },
                # Existing
                *[
                    {
                        'id': self.gID(membership.id),
                        'clientId': f'client-id-existings-{membership.id}',
                        'member': membership.member_id,
                        'role': self.genum(ProjectMembership.Role.ADMIN),  # Make everyone admin
                    }
                    for membership in to_be_modified_memberships
                ],
            ],
            'delete_ids': [
                self.gID(membership.id)
                for membership in to_be_deleted_memberships
            ],
        }
        content = self.query_check(self.Mutation.ProjectMembershipBulkUpdate, variables=variables, assert_errors=True)
        assert content['data'] is None

        self.force_login(user)
        for role, has_access in [
            # With login - No membership
            (None, False),
            # With login - Normal membership
            (ProjectMembership.Role.MEMBER, False),
            # With login - Admin membership
            (ProjectMembership.Role.ADMIN, True),
        ]:
            if role is not None:
                project.add_member(user, role=role)
            content = self.query_check(self.Mutation.ProjectMembershipBulkUpdate, variables=variables)
            if not has_access:
                if role is None:
                    assert content['data']['private']['projectScope'] is None
                else:
                    content_response = content['data']['private']['projectScope']['updateMemberships']
                    assert content_response['errors'] is not None, content_response
                    assert content_response['results'] is None, content_response
                    assert content_response['deleted'] is None, content_response
                continue

            content_response = content['data']['private']['projectScope']['updateMemberships']
            assert content_response == {
                'errors': [
                    [
                        {
                            'array_errors': None,
                            'client_id': 'client-new-id',
                            'field': 'nonFieldErrors',
                            'messages': 'Membership already exists.',
                            'object_errors': None
                        }
                    ]
                ],
                'results': [
                    {
                        'id': self.gID(
                            ProjectMembership.objects.filter(
                                project=project,
                                member=to_be_member_user.id,
                            ).first().id
                        ),
                        'clientId': 'client-new-id',
                        'memberId': self.gID(to_be_member_user.id),
                        'role': 'MEMBER'
                    },
                    *[
                        {
                            'id': self.gID(membership.id),
                            'clientId': f'client-id-existings-{membership.id}',
                            'memberId': self.gID(membership.member_id),
                            'role': self.genum(ProjectMembership.Role.ADMIN),
                        }
                        for membership in to_be_modified_memberships
                    ]
                ],
                'deleted': [
                    {
                        'id': self.gID(membership.id),
                        'clientId': self.gID(membership.id),
                        'memberId': self.gID(membership.member_id),
                        'role': self.genum(ProjectMembership.Role(membership.role)),
                    }
                    for membership in to_be_deleted_memberships
                ],
            }, content_response

    def test_project_membership_leave(self):
        user = UserFactory.create()
        # NOTE: created_by/modified_by != membership
        project = ProjectFactory.create(created_by=user, modified_by=user)
        self_membership = project.add_member(user, role=ProjectMembership.Role.ADMIN)

        variables = {
            'project_id': project.id,
            'items': [
                {
                    # With id
                    'id': self_membership.id,
                    'clientId': 'self-membership-with-id',
                    'member': user.id,
                    'role': self.genum(ProjectMembership.Role.MEMBER),
                },
                {
                    # Without id
                    'clientId': 'self-membership-without-id',
                    'member': user.id,
                    'role': self.genum(ProjectMembership.Role.MEMBER),
                },
            ],
            'delete_ids': [self.gID(self_membership.id)],
        }

        self.force_login(user)
        # -- Make sure user can't mutate self membership
        content = self.query_check(self.Mutation.ProjectMembershipBulkUpdate, variables=variables)
        content_response = content['data']['private']['projectScope']['updateMemberships']
        assert content_response == {
            'errors': [
                [
                    {
                        'array_errors': None,
                        'client_id': 'self-membership-with-id',
                        'field': 'nonFieldErrors',
                        'messages': 'Membership already exists.',
                        'object_errors': None
                    },
                ],
                [
                    {
                        'array_errors': None,
                        'client_id': 'self-membership-without-id',
                        'field': 'nonFieldErrors',
                        'messages': 'Membership already exists.',
                        'object_errors': None
                    }
                ]
            ],
            'results': [],
            'deleted': [],
        }, content_response

        # -- Using leave node to remove membership
        variables = {
            'project_id': project.id,
            'confirm_password': 'wrong-password',
            # 'confirm_password': user.password_text,
        }
        content = self.query_check(self.Mutation.ProjectMembershipLeave, variables=variables)
        content_response = content['data']['private']['projectScope']['leaveProject']
        assert content_response == {
            'ok': False,
            'errors': [{
                'array_errors': None,
                'field': 'nonFieldErrors',
                'messages': "Password didn't match",
                'object_errors': None
            }],
        }
        self_membership.refresh_from_db()  # Shouldn't throw any error

        # Now with correct password
        variables['confirm_password'] = user.password_text
        content = self.query_check(self.Mutation.ProjectMembershipLeave, variables=variables)
        content_response = content['data']['private']['projectScope']['leaveProject']
        assert content_response == {
            'ok': True,
            'errors': None,
        }
        with self.assertRaises(ProjectMembership.DoesNotExist):
            self_membership.refresh_from_db()

        # Again without membership
        content = self.query_check(self.Mutation.ProjectMembershipLeave, variables=variables)
        assert content['data']['private']['projectScope'] is None
