from .bases import SecretBackend
from aiovault.exceptions import InvalidPath, InvalidRequest
from aiovault.objects import Value
from aiovault.util import base64_encode, ok, task


class ConsulBackend(SecretBackend):

    @task
    def config_access(self, address, token):
        """Configures the access information for Consul.

        This is a root protected endpoint.

        Parameters:
            address (str): The address of the Consul instance,
                           provided as scheme://host:port
            token (str): The Consul ACL token to use.
                         Must be a management type token.
        Results:
            bool
        """
        method = 'POST'
        path = self.path('config/access')
        scheme = None
        if address.startswith('https://'):
            scheme, address = 'https', address[8:]
        elif address.startswith('http://'):
            scheme, address = 'http', address[7:]
        data = {'address': address,
                'token': token,
                'scheme': scheme}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
    def read_role(self, name):
        """Queries a Consul role definition.

        Parameters:
            name (str): The role name
        Results:
            Value
        """
        method = 'GET'
        path = self.path('roles', name)

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            return Value(**result)
        except (InvalidPath, InvalidRequest):
            raise KeyError('%r does not exists' % name)

    @task
    def write_role(self, name, *, policy):
        """Creates or updates the Consul role definition.

        Parameters:
            name (str): The role name
            policy (str): The Consul ACL policy.
        Returns:
            bool
        """
        method = 'POST'
        path = self.path('roles', name)
        data = {'policy': base64_encode(policy)}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
    def delete_role(self, name):
        """Deletes a Consul role definition.

        Parameters:
            name (str): The role name
        Returns:
            bool
        """
        method = 'DELETE'
        path = self.path('roles', name)

        response = yield from self.req_handler(method, path)
        return ok(response)

    @task
    def creds(self, name):
        """Generates a dynamic Consul token based on the role definition.

        Parameters:
            name (str): The role name
        Results:
            Value
        """
        method = 'GET'
        path = self.path('creds', name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Value(**result)
