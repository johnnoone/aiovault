"""
    auth
    ~~~~

"""

import asyncio
from .backends import load_backend, load_login
from collections.abc import Mapping

__all__ = ['AuthEndpoint', 'AuthCollection']


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

        Returns:
            AuthCollection
        """
        method = 'GET'
        path = '/sys/auth'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return AuthCollection(result, self.req_handler)

    @asyncio.coroutine
    def get(self, name):
        """Returns auth backend.

        Parameters:
            name (str): The auth backend name
        Returns
            dict
        """
        name = getattr(name, 'name', name)
        method = 'GET'
        path = '/sys/auth'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        data = result['%s/' % name]
        return load_backend(data['type'], {
            'name': name,
            'req_handler': self.req_handler
        })

    @asyncio.coroutine
    def enable(self, name, *, type=None, description=None):
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


class AuthCollection(Mapping):

    def __init__(self, backends, req_handler):
        self.backends = backends
        self.req_handler = req_handler

    def __getitem__(self, name):
        path = '%s/' % name
        return load_backend(self.backends[path]['type'], {
            'name': name,
            'req_handler': self.req_handler
        })

    def __iter__(self):
        for key in self.backends.keys():
            yield key[:-1]

    def __len__(self):
        return len(self.backends)

    def __repr__(self):
        data = tuple(self.backends.keys())
        return '<AuthCollection{!r}>'.format(data)
