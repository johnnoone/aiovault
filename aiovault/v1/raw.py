import json
from aiovault.exceptions import InvalidPath
from aiovault.objects import Value
from aiovault.util import suppress, task


class RawEndpoint:
    """

    .. note:: This is the raw path in the storage backend and not the logical
              path that is exposed via the mount system.

    """

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @task
    def read(self, key):
        """Reads the value of the key at the given path.

        Parameters:
            path (str): The key name
        Returns:
            Value: The key value
        """
        method = 'GET'
        path = '/sys/raw/%s' % key

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
        path = '/sys/raw/%s' % key
        data = {'value': json.dumps(value)}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def delete(self, key):
        """Ensure that key is absent with given path.

        Parameters:
            path (str): The key name
        Returns:
            bool: The key does not exists in storage
        """
        method = 'DELETE'
        path = '/sys/raw/%s' % key

        response = yield from self.req_handler(method, path)
        return response.status == 204
