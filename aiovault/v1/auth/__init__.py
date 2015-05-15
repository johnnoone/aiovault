import asyncio
from .backends import load_backend, load_login


class AuthEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @asyncio.coroutine
    def login(self, endpoint, **credentials):
        res = load_login(endpoint, {
            'name': endpoint,
            'req_handler': self.req_handler
        }, credentials)
        return res

    @asyncio.coroutine
    def items(self):
        """Lists all the enabled auth backends.
        """
        method = 'GET'
        path = '/sys/auth'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def load(self, name):
        method = 'GET'
        path = '/sys/auth'

        if name.endswith('/'):
            mount, name = name, name[:-1]
        else:
            mount = name + '/'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        data = result[mount]
        return load_backend(data['type'], {
            'name': name,
            'req_handler': self.req_handler
        })

    @asyncio.coroutine
    def add(self, name, *, type=None, description=None):
        """Enable a new auth backend.

        The auth backend can be accessed and configured via the mount
        point specified in the URL. This mount point will be exposed
        under the auth prefix. For example, enabling with the
        ``/sys/auth/foo`` URL will make the backend available at ``/auth/foo``.

        Parameters:
            name (str): The name of mount
            type (str): The name of the auth backend type, such as ``github``
            description (str): A human-friendly description of the auth backend
        """
        name = getattr(name, 'name', name)
        type = type or name
        method = 'POST'
        path = '/sys/auth/%s' % name
        data = {'type': type,
                'description': description}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @asyncio.coroutine
    def delete(self, name):
        """Disable the auth backend at the given mount point.

        Parameters:
            name (str): The name of mount
        """
        method = 'DELETE'
        path = '/sys/auth/%s' % name

        response = yield from self.req_handler(method, path)
        return response.status == 204
