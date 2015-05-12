import asyncio
from abc import ABCMeta
from aiovault.exceptions import InvalidPath
from aiovault.objects import Value


class SecretBackend(metaclass=ABCMeta):

    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @asyncio.coroutine
    def help(self):
        """Returns help for this backend.

        .. note:: You must be logged with the good policies
        """
        method = 'GET'
        path = '/sys/auth/%s/' % self.name
        params = {'help': 1}

        response = yield from self.req_handler(method, path, params=params)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def read(self, key):
        """Reads the value of the key at the given path.

        Parameters:
            key (str): The key to read
        Returns:
            Value: The key value
        """
        method = 'GET'
        path = '/%s/%s' % (self.name, key)

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            return Value(**result)
        except InvalidPath:
            raise KeyError('%r does not exists' % key)

    @asyncio.coroutine
    def write(self, key, values):
        """Update the value of the key at the given path.

        Parameters:
            key (str): The key to read
            values (dict): The data to write
        Returns:
            bool: The key has been written
        """
        if not isinstance(values, dict):
            raise ValueError('values must be a dict')
        method = 'POST'
        path = '/%s/%s' % (self.name, key)
        data = values

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @asyncio.coroutine
    def delete(self, key):
        """Ensure that key is absent with given path.

        Parameters:
            path (str): The key name
        Returns:
            bool: The key does not exists in storage
        """
        method = 'DELETE'
        path = '/%s/%s' % (self.name, key)

        response = yield from self.req_handler(method, path)
        return response.status == 204

    def __repr__(self):
        return '<%s(name=%r)>' % (self.__class__.__name__, self.name)
