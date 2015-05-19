import asyncio
from .bases import SecretBackend


class ConsulBackend(SecretBackend):

    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @asyncio.coroutine
    def config_access(self, address, token):
        """Configures the access information for Consul.

        This is a root protected endpoint.

        Parameters:
            address (str): The address of the Consul instance,
                           provided as scheme://host:port
            token (str): The Consul ACL token to use.
                         Must be a management type token.
        """
        method = 'POST'
        path = '/%s/config/access' % self.name
        scheme = None
        if address.startswith('https://'):
            scheme, address = 'https', address[8:]
        elif address.startswith('http://'):
            scheme, address = 'http', address[7:]
        data = {'address': address,
                'token': token,
                'scheme': scheme}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def read_role(self, name):
        """Queries a Consul role definition.

        Parameters:
            name (str): The role name
        """
        method = 'GET'
        path = '/%s/roles/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def write_role(self, name, policy):
        """Creates or updates the Consul role definition.

        Parameters:
            name (str): The role name
            policy (str): The base64 encoded Consul ACL policy.
        """
        method = 'POST'
        path = '/%s/roles/%s' % (self.name, name)
        data = {'policy': policy}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def delete_role(self, name):
        """Deletes a Consul role definition.

        Parameters:
            name (str): The role name
        """
        method = 'DELETE'
        path = '/%s/roles/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def creds(self, name):
        """Generates a dynamic Consul token based on the role definition.

        Parameters:
            name (str): The role name
        """
        method = 'GET'
        path = '/%s/creds/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result
