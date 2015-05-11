import asyncio
from .bases import AuthBackend


class AppIDBackend(AuthBackend):

    @asyncio.coroutine
    def login(self, username, password):
        """Returns information about the current client token.
        """
        method = 'POST'
        path = '/auth/%s/login/%s' % (self.name, username)
        data = {'password': password}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def create(self, username, password, policies):
        """The above creates a new user.

        Parameters:
            username (str):
            password (str):
            policies (str):
        """
        method = 'POST'
        path = '/auth/%s/users/%s' % (self.name, username)
        data = {'password': password,
                'policies': policies}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def create_app(self, app, display_name, policies):
        """docstring for create_app_id"""
        app = getattr(app, 'id', app)
        method = 'POST'
        path = '/auth/%s/map/app-id/%s' % (self.name, app)
        data = {'display_name': display_name,
                'policies': policies}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def create_user(self, user, app, cidr_block=None):
        """docstring for create_app_id"""
        app = getattr(app, 'id', app)
        user = getattr(user, 'id', user)
        method = 'POST'
        path = '/auth/%s/map/user-id/%s' % (self.name, user)
        data = {'app': app,
                'cidr_block': cidr_block}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result
