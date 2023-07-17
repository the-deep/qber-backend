from typing import Dict
from enum import Enum

from django.test import TestCase as BaseTestCase
from django.db import models


class TestCase(BaseTestCase):
    def force_login(self, user):
        self.client.force_login(user)

    def logout(self):
        self.client.logout()

    def query_check(
        self,
        query: str,
        assert_errors: bool = False,
        variables: dict | None = None,
        **kwargs,
    ) -> Dict:
        response = self.client.post(
            "/graphql/",
            data={
                "query": query,
                "variables": variables,
            },
            content_type="application/json",
            **kwargs,
        )
        if assert_errors:
            self.assertResponseHasErrors(response)
        else:
            self.assertResponseNoErrors(response)
        return response.json()

    def assertResponseNoErrors(self, resp, msg=None):
        """
        Assert that the call went through correctly. 200 means the syntax is ok,
        if there are no `errors`,
        the call was fine.
        :resp HttpResponse: Response
        """
        content = resp.json()
        self.assertEqual(resp.status_code, 200, msg or content)
        self.assertNotIn("errors", list(content.keys()), msg or content)

    def assertResponseHasErrors(self, resp, msg=None):
        """
        Assert that the call was failing. Take care: Even with errors,
        GraphQL returns status 200!
        :resp HttpResponse: Response
        """
        content = resp.json()
        self.assertIn("errors", list(content.keys()), msg or content)

    def genum(self, _enum: models.TextChoices | models.IntegerChoices | Enum):
        """
        Return appropriate enum value.
        """
        return _enum.name
