import asyncio
import json
from .bases import SecretBackend


class AWSBackend(SecretBackend):

    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @asyncio.coroutine
    def config_root(self, access_key, secret_key, region):
        """Configures the root IAM credentials used.

        This is a root protected endpoint.

        Parameters:
            access_key (str): The AWS Access Key
            secret_key (str): The AWS Secret Key
            region (str): The AWS region for API calls
        """
        method = 'POST'
        path = '/%s/config/root' % self.name
        data = {'access_key': access_key,
                'secret_key': secret_key,
                'region': region}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def config_lease(self, lease, lease_max):
        """Configures the lease settings for generated credentials.

        This is a root protected endpoint.

        Parameters:
            lease (str): The lease value provided as a string duration with
                         time suffix. Hour is the largest suffix.
            lease_max (str): The maximum lease value provided as a string
                             duration with time suffix. Hour is the largest
                             suffix.
        """
        method = 'POST'
        path = '/%s/config/lease' % self.name
        data = {'lease': lease,
                'lease_max': lease_max}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def write_role(self, name, policy):
        """Creates or updates a named role.

        Parameters:
            name (str): The role name.
            policy (obj): The IAM policy.
        """
        method = 'POST'
        path = '/%s/roles/%s' % (self.name, name)
        data = {'policy': json.dumps(policy)}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def read_role(self, name):
        """Queries a named role.

        Parameters:
            name (str): The role name.
        """
        method = 'GET'
        path = '/%s/roles/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def delete_role(self, name):
        """Queries a named role.

        Parameters:
            name (str): The role name.
        """
        method = 'DELETE'
        path = '/%s/roles/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def creds(self, name):
        """Generates a dynamic IAM credential based on the named role.

        Parameters:
            name (str): The role name.
        """
        method = 'GET'
        path = '/%s/creds/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result
