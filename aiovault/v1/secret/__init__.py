"""
    secret
    ~~~~~~

"""

import logging
from .backends import load_backend
from collections.abc import Mapping
from aiovault.exceptions import InternalServerError
from aiovault.util import task

__all__ = ['SecretEndpoint', 'SecretCollection']


class SecretEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @task
    def items(self):
        """Lists all the mounted secret backends

        Returns:
            SecretCollection
        """
        method = 'GET'
        path = '/sys/mounts'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return SecretCollection(result, self.req_handler)

    def load(self, name, *, type=None):
        """Get a backend by its name

        Parameters:
            name (str): The backed name
            type (str): The name of the backend type, such as ``aws``
        Returns:
            SecretBackend
        """
        type = type or getattr(name, 'type', name)
        name = getattr(name, 'name', name)
        return load_backend(type, {
            'name': name,
            'type': type,
            'req_handler': self.req_handler
        })

    @task
    def mount(self, name, *, type=None, description=None):
        """Load and mount a new secret backend

        Parameters:
            name (str): The name of mount
            type (str): The name of the backend type, such as ``aws``
            description (str): A human-friendly description of the mount
        Returns:
            (bool, SecretBackend)
        """
        backend = self.load(name, type=type)
        try:
            yield from backend.mount(description=description)
            return True, backend
        except Exception as error:
            logging.exception(error)
            return False, backend

    @task
    def unmount(self, name):
        """Unmount a secret backend

        Parameters:
            name (str): The name of mounted backend
        Returns:
            bool
        """
        name = getattr(name, 'name', name)
        method = 'DELETE'
        path = '/sys/mounts/%s' % name

        try:
            response = yield from self.req_handler(method, path)
            return response.status == 204
        except InternalServerError:
            return False

    @task
    def remount(self, src, dest):
        """Move the secret backend

        Parameters:
            src (str): The endpoint to be moved
            dest (str): The new endpoint
        Returns:
            bool
        """
        src = getattr(src, 'name', src)
        dest = getattr(dest, 'name', dest)
        method = 'POST'
        path = '/sys/remount'
        data = {'from': src,
                'to': dest}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204


class SecretCollection(Mapping):

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
