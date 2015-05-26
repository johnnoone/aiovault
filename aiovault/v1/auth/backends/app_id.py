from .bases import AuthBackend
from aiovault.objects import Value, WrittenToken
from aiovault.util import format_policies, task


class AppIDBackend(AuthBackend):

    @task
    def login(self, *, app_id, user_id):
        """Returns information about the current client token.

        Parameters:
            app_id (str): The app id
            user_id (str): The user id
        Returns:
            WrittenToken: The client token
        """
        method = 'POST'
        path = '/auth/%s/login' % self.name
        data = {'app_id': app_id,
                'user_id': user_id}

        response = yield from self.req_handler(method, path, json=data)
        result = yield from response.json()
        return WrittenToken(**result)

    @task
    def read_app(self, app_id):
        """Read app.

        Parameters:
            app_id (str): The application ID
        Returns:
            Value
        """
        app_id = getattr(app_id, 'id', app_id)
        method = 'GET'
        path = '/auth/%s/map/app-id/%s' % (self.name, app_id)
        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Value(**result)

    @task
    def write_app(self, app_id, *, policies=None, display_name=None):
        """Write app.

        Parameters:
            app_id (str): The application ID
            policies (str): The policies
            display_name (str): The name to be displayed
        Returns:
            bool
        """
        app_id = getattr(app_id, 'id', app_id)
        method = 'POST'
        path = '/auth/%s/map/app-id/%s' % (self.name, app_id)
        policies = format_policies(policies)

        data = {'display_name': display_name or app_id,
                'value': policies}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def write_user(self, user, app_id, cidr_block=None):
        """Write user.

        Parameters:
            user (str): The user name
            app_id (str): The application ID
            cidr_block (str): The CIDR block to limit
        Returns:
            bool
        """
        app_id = getattr(app_id, 'id', app_id)
        user = getattr(user, 'id', user)
        method = 'POST'
        path = '/auth/%s/map/user-id/%s' % (self.name, user)
        data = {'value': app_id,
                'cidr_block': cidr_block}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204
