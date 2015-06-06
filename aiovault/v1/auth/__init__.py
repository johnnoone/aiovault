"""
    auth
    ~~~~

"""

from .backends import load_backend
from collections.abc import Mapping
from aiovault.util import ok, task

__all__ = ['authenticate', 'AuthEndpoint', 'AuthCollection']


class AuthEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @task
    def items(self):
        """Lists all the enabled auth backends

        Returns:
            AuthCollection
        """
        method = 'GET'
        path = '/sys/auth'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return AuthCollection(result, self.req_handler)

    def load(self, name, *, type=None):
        """Returns auth backend

        Parameters:
            name (str): The auth backend name
        Returns
            AuthBackend
        """
        type = type or getattr(name, 'type', name)
        name = getattr(name, 'name', name)

        return load_backend(type, {
            'name': name,
            'type': type,
            'req_handler': self.req_handler
        })

    @task
    def login(self, name, *, type=None, **credentials):
        """Login

        Parameters:
            name (str): The name of mount
            type (str): The name of the auth backend type, such as ``github``
            credentials (str): Login credentials
        Returns
            AuthBackend
        """
        backend = self.load(name, type=type)
        try:
            token = yield from backend.login(**credentials)
            return token
        except AttributeError:
            return NotImplemented

    @task
    def enable(self, name, *, type=None, description=None):
        """Enable and load a new auth backend

        Parameters:
            name (str): The name of mount
            type (str): The name of the auth backend type, such as ``github``
            description (str): A human-friendly description of the auth backend
        Returns
            AuthBackend
        """
        backend = self.load(name, type=type)
        enabled = yield from backend.enable(description)
        if enabled:
            return backend

    @task
    def disable(self, name):
        """Disable the auth backend at the given mount point

        Parameters:
            name (str): The name of mount
        """
        method = 'DELETE'
        path = '/sys/auth/%s' % name

        response = yield from self.req_handler(method, path)
        return ok(response)


class AuthCollection(Mapping):

    def __init__(self, backends, req_handler):
        self.backends = backends
        self.req_handler = req_handler

    def __getitem__(self, name):
        path = '%s/' % name
        return load_backend(self.backends[path]['type'], {
            'name': name,
            'type': self.backends[path]['type'],
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
