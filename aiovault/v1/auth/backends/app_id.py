from .bases import AuthBackend
from aiovault.objects import Value
from aiovault.token import authenticate
from aiovault.util import format_policies, ok, task, extract_id, extract_name


class AppIDBackend(AuthBackend):

    @task
    def login(self, *, app, user):
        """Returns information about the current client token.

        Parameters:
            app (str): The application ID
            user (str): The user name
        Returns:
            LoginToken: The client token
        """
        method = 'POST'
        path = self.path('login')
        app = extract_id(app)
        user = extract_name(user)
        data = {'app_id': app,
                'user_id': user}

        token = yield from authenticate(self.req_handler,
                                        method,
                                        path,
                                        json=data)
        return token

    @task
    def read_app(self, app):
        """Read app.

        Parameters:
            app (str): The application ID
        Returns:
            Value
        """
        app = extract_id(app)
        method = 'GET'
        path = self.path('map', 'app-id', app)
        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Value(**result)

    @task
    def write_app(self, app, *, policies=None, display_name=None):
        """Write app.

        Parameters:
            app (str): The application ID
            policies (list): The policies
            display_name (str): The name to be displayed
        Returns:
            bool
        """
        app = extract_id(app)
        method = 'POST'
        path = self.path('map', 'app-id', app)
        policies = format_policies(policies)

        data = {'display_name': display_name or app,
                'value': policies}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
    def delete_app(self, app):
        """Delete app.

        Parameters:
            app (str): The application ID
        Returns:
            bool
        """
        app = extract_id(app)
        method = 'DELETE'
        path = self.path('map', 'app-id', app)
        response = yield from self.req_handler(method, path)
        return ok(response)

    @task
    def read_user(self, user):
        """Read user.

        Parameters:
            user (str): The user name
        Returns:
            Value
        """
        user = extract_id(user)
        method = 'GET'
        path = self.path('map', 'user-id', user)
        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Value(**result)

    @task
    def write_user(self, user, app, cidr_block=None):
        """Write user.

        Parameters:
            user (str): The user name
            app (str): The application ID
            cidr_block (str): The CIDR block to limit
        Returns:
            bool
        """
        app = extract_id(app)
        user = extract_name(user)
        method = 'POST'
        path = self.path('map', 'user-id', user)
        data = {'value': app,
                'cidr_block': cidr_block}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
    def delete_user(self, user):
        """Delete user.

        Parameters:
            user (str): The user name
        Returns:
            bool
        """
        user = extract_id(user)
        method = 'DELETE'
        path = self.path('map', 'user-id', user)
        response = yield from self.req_handler(method, path)
        return ok(response)
