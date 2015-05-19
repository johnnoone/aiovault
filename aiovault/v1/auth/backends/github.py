import asyncio
from .bases import AuthBackend
from aiovault.objects import WrittenToken
from aiovault.util import format_policies, task


class GitHubBackend(AuthBackend):

    @task
    def login(self, *, github_token):
        """Log with github.

        Parameters:
            github_token (str): GitHub personal API token
        Returns:
            WrittenToken
        """
        method = 'POST'
        path = '/auth/%s/login' % self.name
        data = {'token': github_token}

        response = yield from self.req_handler(method, path, json=data)
        result = yield from response.json()
        return WrittenToken(**result)

    @asyncio.coroutine
    def configure(self, *, organization):
        """Configure github organization.

        Parameters:
            organization (str): The organization name a user must be a part of
                                to authenticate
        Returns:
            bool
        """
        method = 'POST'
        path = '/auth/%s/config' % self.name
        data = {'organization': organization}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @asyncio.coroutine
    def write_team(self, name, policies):
        """Configure github team.

        Parameters:
            name (str): The team name
            policies (str): The team policies
        Returns:
            bool
        """
        method = 'POST'
        path = '/auth/%s/map/teams/%s' % (self.name, name)
        policies = format_policies(policies)
        data = {'value': policies}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204
