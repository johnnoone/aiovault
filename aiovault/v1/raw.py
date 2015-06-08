import json
from aiovault.exceptions import InvalidPath
from aiovault.objects import Value
from aiovault.util import suppress, ok, task, Path


class RawEndpoint:
    """

    .. note:: This is the raw path in the storage backend and not the logical
              path that is exposed via the mount system.

    """

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @property
    def path(self):
        return Path('/sys/raw')

    @task
    def read(self, key):
        """Reads the value of the key at the given path.

        Parameters:
            path (str): The key name
        Returns:
            Value: The key value
        """
        method = 'GET'
        path = self.path(key)

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            with suppress(KeyError):
                result['data']['value'] = json.loads(result['data']['value'])
            return Value(**result)
        except InvalidPath:
            raise KeyError('%r does not exists' % path)

    @task
    def write(self, key, value):
        """Update the value of the key at the given path.

        Parameters:
            path (str): The key name
            value (obj): The value of the key.
        Returns:
            bool: The key has been written
        """
        method = 'PUT'
        path = self.path(key)
        data = {'value': json.dumps(value)}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
    def delete(self, key):
        """Ensure that key is absent with given path.

        Parameters:
            path (str): The key name
        Returns:
            bool: The key does not exists in storage
        """
        method = 'DELETE'
        path = self.path(key)

        response = yield from self.req_handler(method, path)
        return ok(response)
