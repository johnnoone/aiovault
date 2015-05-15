import asyncio
from .bases import AuthBackend
from aiovault.objects import WrittenToken
from aiovault.util import task


class AppIDBackend(AuthBackend):

    @task
    def login(self, app_id, user_id):
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

    @asyncio.coroutine
    def create_app(self, app_id, *, policies=None, display_name=None):
        """docstring for create_app_id"""
        app_id = getattr(app_id, 'id', app_id)
        method = 'POST'
        path = '/auth/%s/map/app-id/%s' % (self.name, app_id)

        if policies and isinstance(policies, (list, set, tuple)):
            policies = ','.join(policies)

        data = {'display_name': display_name or app_id,
                'value': policies}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @asyncio.coroutine
    def create_user(self, user, app_id, cidr_block=None):
        """docstring for create_app_id"""
        app_id = getattr(app_id, 'id', app_id)
        user = getattr(user, 'id', user)
        method = 'POST'
        path = '/auth/%s/map/user-id/%s' % (self.name, user)
        data = {'value': app_id,
                'cidr_block': cidr_block}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204
