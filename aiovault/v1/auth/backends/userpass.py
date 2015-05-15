import asyncio
from .bases import AuthBackend
from aiovault.objects import WrittenToken
from aiovault.util import task


class UserPassBackend(AuthBackend):

    @task
    def login(self, username, password):
        """Returns information about the current client token.

        Parameters:
            username (str): The username
            password (str): The password
        Returns:
            WrittenToken
        """
        method = 'POST'
        path = '/auth/%s/login/%s' % (self.name, username)
        data = {'password': password}

        response = yield from self.req_handler(method, path, json=data)
        result = yield from response.json()
        return WrittenToken(**result)

    @asyncio.coroutine
    def create(self, username, password, policies=None):
        """The above creates a new user.

        Parameters:
            username (str): The username
            password (str): The password
            policies (str): The policies associated with the user
        """
        method = 'POST'
        path = '/auth/%s/users/%s' % (self.name, username)
        data = {'password': password,
                'policies': policies}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204
