
class RawEndpoint:

    def get(self, path):
        """Reads the value of the key at the given path.

        This is the raw path in the storage backend and not the logical
        path that is exposed via the mount system.

        Parameters:
            path (str): The key name
        """
        method = 'GET'
        path = '/sys/raw/%s' % path

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    def put(self, path, value):
        """Update the value of the key at the given path.

        This is the raw path in the storage backend and not the logical
        path that is exposed via the mount system.

        Parameters:
            path (str): The key name
            value (obj): The value of the key.
        """
        method = 'PUT'
        path = '/sys/raw/%s' % path
        data = {'value': value}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    def delete(self, path):
        """Delete the key with given path.

        This is the raw path in the storage backend and not the logical
        path that is exposed via the mount system.

        Parameters:
            path (str): The key name
        """
        method = 'DELETE'
        path = '/sys/raw/%s' % path

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result
