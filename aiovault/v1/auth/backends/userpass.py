from .bases import AuthBackend
from aiovault.token import authenticate
from aiovault.util import ok, task


class UserPassBackend(AuthBackend):
    """Log in with a username and password.

    The "userpass" credential provider allows authentication using
    a combination of a username and password. No additional factors
    are supported.

    The username/password combination is configured using the "users/"
    endpoints by a user with root access. Authentication is then done
    by suppying the two fields for "login".
    """

    @task
    def login(self, *, username, password):
        """Returns information about the current client token.

        Parameters:
            username (str): The username
            password (str): The password
        Returns:
            LoginToken
        """
        method = 'POST'
        path = self.path('login', username)
        data = {'password': password}

        token = yield from authenticate(self.req_handler,
                                        method,
                                        path,
                                        json=data)
        return token

    @task
    def create(self, username, password, policies=None):
        """The above creates a new user.

        Parameters:
            username (str): The username
            password (str): The password
            policies (str): The policies associated with the user
        """
        method = 'POST'
        path = self.path('users', username)
        data = {'password': password,
                'policies': policies}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)
