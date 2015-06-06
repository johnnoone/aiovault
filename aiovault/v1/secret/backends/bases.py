from abc import ABCMeta
from aiovault.exceptions import HTTPError, MountError
from aiovault.util import ok, task


class SecretBackend(metaclass=ABCMeta):

    def __init__(self, name, type, req_handler):
        self.name = name
        self.type = type
        self.req_handler = req_handler

    @task
    def mount(self, *, name=None, description=None):
        """Mount a new secret backend

        Parameters:
            name (str): The new endpoint
            description (str): A human-friendly description of the mount
        """
        name = name or self.name
        method = 'POST'
        path = '/sys/mounts/%s' % name
        data = {'type': self.type,
                'description': description}

        try:
            response = yield from self.req_handler(method, path, json=data)
            if ok(response):
                self.name = name
                return
        except HTTPError as error:
            raise MountError(*error.errors)
        raise MountError

    @task
    def unmount(self):
        """Unmount the secret backend
        """
        method = 'DELETE'
        path = '/sys/mounts/%s' % self.name

        try:
            response = yield from self.req_handler(method, path)
            if ok(response):
                return
        except HTTPError as error:
            raise MountError(*error.errors)
        raise MountError

    @task
    def remount(self, dest):
        """Move the secret backend

        Parameters:
            dest (str): The new endpoint
        """
        dest = getattr(dest, 'name', dest)
        method = 'POST'
        path = '/sys/remount'
        data = {'from': self.name,
                'to': dest}

        try:
            response = yield from self.req_handler(method, path, json=data)
            if ok(response):
                self.name = dest
                return
        except HTTPError as error:
            raise MountError(*error.errors)
        raise MountError

    def __repr__(self):
        return '<%s(name=%r)>' % (self.__class__.__name__, self.name)
