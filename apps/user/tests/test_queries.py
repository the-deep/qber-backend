from main.tests import TestCase

from apps.user.models import User
from apps.user.factories import UserFactory


class TestUserQuery(TestCase):
    def test_me(self):
        query = '''
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

        User.objects.all().delete()  # Clear all users if exists
        # Create some users
        user = UserFactory.create(
            email_opt_outs=[User.OptEmailNotificationType.NEWS_AND_OFFERS],
        )
        # Some other users as well
        UserFactory.create_batch(3)

        # Without authentication -----
        content = self.query_check(query)
        assert content['data']['public']['me'] is None

        # With authentication -----
        self.force_login(user)
        content = self.query_check(query)
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
