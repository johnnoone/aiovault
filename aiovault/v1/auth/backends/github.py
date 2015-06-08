from .bases import AuthBackend
from aiovault.token import authenticate
from aiovault.util import format_policies, ok, task


class GitHubBackend(AuthBackend):

    @task
    def login(self, *, github_token):
        """Log with github.

        Parameters:
            github_token (str): GitHub personal API token
        Returns:
            LoginToken
        """
        method = 'POST'
        path = self.path('login')
        data = {'token': github_token}

        token = yield from authenticate(self.req_handler,
                                        method,
                                        path,
                                        json=data)
        return token

    @task
    def configure(self, *, organization):
        """Configure github organization.

        Parameters:
            organization (str): The organization name a user must be a part of
                                to authenticate
        Returns:
            bool
        """
        method = 'POST'
        path = self.path('config')
        data = {'organization': organization}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
    def write_team(self, name, policies):
        """Configure github team.

        Parameters:
            name (str): The team name
            policies (str): The team policies
        Returns:
            bool
        """
        method = 'POST'
        path = self.path('map', 'teams', name)
        policies = format_policies(policies)
        data = {'value': policies}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)
