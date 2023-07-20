from main.tests import TestCase

from apps.project.models import ProjectMembership

from apps.user.factories import UserFactory
from apps.project.factories import ProjectFactory


class TestProjectQuery(TestCase):
    class Query:
        ProjectList = '''
            query MyQuery {
              private {
                id
                projects (order: {id: ASC}) {
                  count
                  items {
                    id
                    title
                    currentUserRole
                    createdBy {
                      id
                      displayName
                    }
                    modifiedBy {
                      id
                      displayName
                    }
                  }
                }
              }
            }
        '''

        Project = '''
            query MyQuery($projectId: ID!) {
              private {
                id
                projectScope(pk: $projectId) {
                  id
                  project {
                    id
                    title
                    currentUserRole
                    createdBy {
                      id
                      displayName
                    }
                    modifiedBy {
                      id
                      displayName
                    }
                    members(order: {id: ASC}) {
                      count
                      items {
                        id
                        memberId
                        role
                      }
                    }
                  }
                }
              }
            }
        '''

    def test_projects(self):
        # Create some users
        user, *_ = UserFactory.create_batch(4)
        project_f_params = dict(created_by=user, modified_by=user)
        # Create some projects
        projects_with_role = [
            (ProjectMembership.Role.MEMBER, ProjectFactory.create_batch(2, **project_f_params)),
            (ProjectMembership.Role.ADMIN, ProjectFactory.create_batch(3, **project_f_params)),
        ]
        for role, projects in projects_with_role:
            for project in projects:
                project.add_member(user, role=role)

        # Without authentication -----
        content = self.query_check(self.Query.ProjectList, assert_errors=True)
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        content = self.query_check(self.Query.ProjectList)
        assert content['data']['private']['projects'] == dict(
            count=5,
            items=[
                dict(
                    id=str(project.id),
                    title=project.title,
                    currentUserRole=self.genum(role),
                    createdBy=dict(
                        id=str(user.id),
                        displayName=user.get_full_name(),
                    ),
                    modifiedBy=dict(
                        id=str(user.id),
                        displayName=user.get_full_name(),
                    ),
                )
                for role, projects in projects_with_role
                for project in projects
            ],
        )

    def test_project(self):
        # Create some users
        user, user2, user3, *_ = UserFactory.create_batch(4)
        project_f_params = dict(created_by=user, modified_by=user)
        # Create some projects
        project = ProjectFactory.create(**project_f_params)
        project_without_role = ProjectFactory.create(**project_f_params)

        for _user in [user, user2, user3]:
            project.add_member(_user)

        def _query_check(project, **kwargs):
            return self.query_check(
                self.Query.Project,
                variables=dict(
                    projectId=str(project.id),
                ),
                **kwargs,
            )

        # Without authentication -----
        content = _query_check(project, assert_errors=True)
        assert content['data'] is None

        # With authentication -----
        self.force_login(user)
        content = _query_check(project_without_role)
        assert content['data']['private']['projectScope'] is None

        content = _query_check(project)
        assert content['data']['private']['projectScope'] == dict(
            id=str(project.id),
            project=dict(
                id=str(project.id),
                title=project.title,
                currentUserRole=self.genum(ProjectMembership.Role.MEMBER),
                createdBy=dict(
                    id=str(user.id),
                    displayName=user.get_full_name(),
                ),
                modifiedBy=dict(
                    id=str(user.id),
                    displayName=user.get_full_name(),
                ),
                members=dict(
                    count=3,
                    items=[
                        dict(
                            id=str(membership.id),
                            memberId=str(membership.member_id),
                            role=self.genum(ProjectMembership.Role(membership.role)),
                        )
                        for membership in ProjectMembership.objects.filter(project=project).order_by('id')
                    ],
                ),
            ),
        )
