import asyncio
from .bases import AuthBackend


class GitHubBackend(AuthBackend):

    @asyncio.coroutine
    def configure(self, organization):
        """Configure github.

        Parameters:
            organization (str): The organization name a user must be a part of
                                to authenticate
        """
        method = 'POST'
        path = '/auth/%s/config' % self.name
        data = {'organization': organization}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def set_team(self, team, policies):
        """docstring for configure

        Parameters:
            team (str):
            policies (str):
        """
        method = 'POST'
        path = '/auth/%s/map/teams/%s' % (self.name, team)
        data = {'policies': policies}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result
