from .bases import SecretBackend
from aiovault.exceptions import InvalidPath
from aiovault.objects import Value
from aiovault.util import ok, task


class GenericBackend(SecretBackend):
    """Store arbitrary secrets within the configured physical storage.

    The generic backend allows for writing keys with arbitrary values.
    The only value that special is the ``lease`` key, which can be provided
    with any key to restrict the lease time of the secret. This is useful to
    ensure clients periodically renew so that key rolling can be time bounded.
    """

    @task
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

    @task
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
        path = '/%s/%s' % (self.name, key)

        response = yield from self.req_handler(method, path)
        return ok(response)
