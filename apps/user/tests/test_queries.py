from main.tests import TestCase

from apps.user.models import User

from apps.user.factories import UserFactory
from apps.project.factories import ProjectFactory


class TestUserQuery(TestCase):
    class Query:
        ME = '''
            query meQuery {
              public {
                me {
                  id
                  email
                  firstName
                  lastName
                  displayName
                  emailOptOuts
                }
              }
            }
        '''

        USERS = '''
            query MyQuery($filters: UserFilter) {
              private {
                users(pagination: {limit: 10, offset: 0}, filters: $filters) {
                  limit
                  offset
                  count
                  items {
                    id
                    firstName
                    lastName
                    displayName
                  }
                }
              }
            }
        '''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(
            email_opt_outs=[User.OptEmailNotificationType.NEWS_AND_OFFERS],
        )
        # Some other users as well
        cls.users = (
            UserFactory.create(first_name='Test', last_name='Hero', email='sample@test.com'),
            UserFactory.create(first_name='Example', last_name='Villain', email='sample@vil.com'),
            UserFactory.create(first_name='Test', last_name='Hero'),
        )

    def test_me(self):
        # Without authentication -----
        content = self.query_check(self.Query.ME)
        assert content['data']['public']['me'] is None

        user = self.user
        # With authentication -----
        self.force_login(user)
        content = self.query_check(self.Query.ME)
        assert content['data']['public']['me'] == dict(
            id=str(user.id),
            email=user.email,
            firstName=user.first_name,
            lastName=user.last_name,
            displayName=f'{user.first_name} {user.last_name}',
            emailOptOuts=[
                self.genum(opt)
                for opt in user.email_opt_outs
            ],
        )

    def test_users(self):
        project = ProjectFactory.create()
        user1, user2, user3 = self.users
        project.add_member(user1)

        # Without authentication -----
        content = self.query_check(self.Query.USERS, assert_errors=True)
        assert content['data'] is None

        # With authentication -----
        self.force_login(self.user)
        for filters, expected_users in [
            ({'id': {'exact': str(user1.id)}}, [user1]),
            # Free text search tests
            ({'search': 'hero'}, [user1, user3]),
            ({'search': 'test'}, [user1, user3]),
            ({'search': '@vil'}, [user2]),
            ({'search': 'sample'}, [user1, user2]),
            ({'search': 'sample@'}, [user1, user2]),
            ({'membersExcludeProject': str(project.pk)}, [user2, user3]),
        ]:
            content = self.query_check(self.Query.USERS, variables={'filters': filters})
            assert content['data']['private']['users'] == {
                'count': len(expected_users),
                'limit': 10,
                'offset': 0,
                'items': [
                    {
                        'id': str(user.id),
                        'firstName': user.first_name,
                        'lastName': user.last_name,
                        'displayName': f'{user.first_name} {user.last_name}',
                    }
                    for user in expected_users
                ]
            }, (filters, expected_users)
