from .backends import load_backend


class SecretEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    def items(self):
        """Lists all the mounted secret backends.
        """
        method = 'GET'
        path = '/sys/mounts'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()

        for name, data in result.items():
            yield load_backend(name=name,
                               type=data['type'],
                               req_handler=self.req_handler)

    def load(self, name):
        """Get a backend by its name

        Parameters:
            name (str): The backed name
        """
        name = getattr(name, 'name', name)
        method = 'GET'
        path = '/sys/mounts'

        if name.endswith('/'):
            a, b = name, name[:-1]
        else:
            a, b = name + '/', name

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        backend_type = result[a]['type']
        return load_backend(name=b,
                            type=backend_type,
                            req_handler=self.req_handler)

    def mount(self, name, *, type=None, description=None):
        """Mount a new secret backend.

        Parameters:
            name (str): The name of mount
            type  (str): The name of the backend type, such as ``aws``
            description  (str): A human-friendly description of the mount.
        """
        name = getattr(name, 'name', name)
        type = type or name
        method = 'POST'
        path = '/sys/mounts/%s' % name
        data = {'type': type,
                'description': description}

        response = yield from self.req_handler(method, path, data=data)
        return response.status == 204

    def unmount(self, name):
        """Unmount the secret backend.

        Parameters:
            mount_point (str): The name of mount
        """
        name = getattr(name, 'name', name)
        method = 'DELETE'
        path = '/sys/mounts/%s' % name

        response = yield from self.req_handler(method, path)
        return response.status == 204

    def move(self, src, dest):
        """Move the secret backend.

        Parameters:
            src (str): The name to be moved
            dest (str): The new name
        """
        src = getattr(src, 'name', src)
        dest = getattr(dest, 'name', dest)
        method = 'POST'
        path = '/sys/remount'
        data = {'from': src,
                'to': dest}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result
