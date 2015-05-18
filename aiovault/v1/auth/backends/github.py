import asyncio
from .bases import AuthBackend
from aiovault.objects import WrittenToken
from aiovault.util import format_policies, task


class GitHubBackend(AuthBackend):

    @task
    def login(self, *, github_token):
        """Log with github.
        Parameters:
            github_token (str): a github token
        """
        method = 'POST'
        path = '/auth/%s/login' % self.name
        data = {'token': github_token}

        response = yield from self.req_handler(method, path, json=data)
        result = yield from response.json()
        return WrittenToken(**result)

    @asyncio.coroutine
    def configure_organization(self, organization):
        """Configure github organization.

        Parameters:
            organization (str): The organization name a user must be a part of
                                to authenticate
        """
        method = 'POST'
        path = '/auth/%s/config' % self.name
        data = {'organization': organization}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @asyncio.coroutine
    def configure_team(self, team, policies):
        """Configure github team.

        Parameters:
            team (str):
            policies (str):
        """
        method = 'POST'
        path = '/auth/%s/map/teams/%s' % (self.name, team)
        policies = format_policies(policies)
        data = {'value': policies}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204
